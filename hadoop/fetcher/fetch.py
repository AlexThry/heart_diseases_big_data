import config
import pymongo
import time
import os
from datetime import datetime
import logging
import docker
import io
import tarfile
import time


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    client = docker.from_env()

    while True:
        myclient = pymongo.MongoClient(config.MONGO_URL)
        mydb = myclient[config.DB_NAME]
        trees_col = mydb["trees"]  # Use the 'trees' collection for this task

        # Step 1: Fetch patient data from MongoDB (if needed)
        patient_col = mydb["patients"]
        one_hour_ago = int(time.time()) - 3600
        recent_patients = patient_col.find({"timestamp": {"$gte": one_hour_ago}, "output": {"$exists": True}})
        recent_patients_list = list(recent_patients)

        logger.info(f"Fetched {len(recent_patients_list)} patients from the database.")
        logger.info("caca")

        # Step 2: Save data to file for HDFS
        output_dir = datetime.now().strftime("./output/")
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, "patients.txt")

        with open(output_file, "w") as f:
            for patient in recent_patients_list:
                patient.pop("_id", None)
                patient.pop("timestamp", None)
                f.write(str(patient).replace("'", '"') + "\n")

        # Step 3: Copy the file into the Docker container's HDFS system
        container = client.containers.get("namenode")

        with open(output_file, "rb") as f:
            data = f.read()

        tar_stream = io.BytesIO()
        with tarfile.open(fileobj=tar_stream, mode='w') as tar:
            tarinfo = tarfile.TarInfo(name=os.path.basename(output_file))
            tarinfo.size = len(data)
            tar.addfile(tarinfo, io.BytesIO(data))
        tar_stream.seek(0)

        container.put_archive("/tmp", tar_stream)

        # Copy the map_reduce.jar file to the container
        jar_file = "map_reduce.jar"  # Ensure this file exists in your script's directory
        with open(jar_file, "rb") as f:
            jar_data = f.read()

        jar_tar_stream = io.BytesIO()
        with tarfile.open(fileobj=jar_tar_stream, mode='w') as tar:
            tarinfo = tarfile.TarInfo(name=os.path.basename(jar_file))
            tarinfo.size = len(jar_data)
            tar.addfile(tarinfo, io.BytesIO(jar_data))
        jar_tar_stream.seek(0)

        container.put_archive("/tmp", jar_tar_stream)

        container.exec_run("hdfs dfs -mkdir -p /user/root/input")
        logger.info(f"Copied patients info into namenode")

        # Remove old data from HDFS
        container.exec_run("hdfs dfs -rm -f /user/root/input/{}".format(os.path.basename(output_file)))
        logger.info("Removed old patients info from HDFS system")

        # Add the new data into HDFS
        container.exec_run("hdfs dfs -put /tmp/{} /user/root/input/".format(os.path.basename(output_file)))
        logger.info("Added new patients info into HDFS system")

        # Verify if the file is actually in HDFS before running the MapReduce job
        check_input_file = container.exec_run("hdfs dfs -ls /user/root/input/{}".format(os.path.basename(output_file)))
        if check_input_file.exit_code != 0:
            logger.error(f"Input file {os.path.basename(output_file)} not found in HDFS.")
            continue
        else:
            logger.info(f"Input file {os.path.basename(output_file)} is present in HDFS.")


        # Step 4: Check if the output directory exists in HDFS and delete it if necessary
        logger.info("Checking if output directory exists in HDFS...")

        def remove_directory_with_retry(container, retries=3, delay=5):
            for attempt in range(retries):
                check_output_dir = container.exec_run("hdfs dfs -ls /user/root/output")
                if check_output_dir.exit_code == 0:
                    logger.info("Output directory exists. Removing it.")
                    container.exec_run("hdfs dfs -rm -r /user/root/output")

                    # Wait before checking the removal again
                    time.sleep(delay)
                    check_output_dir_after_removal = container.exec_run("hdfs dfs -ls /user/root/output")
                    if check_output_dir_after_removal.exit_code != 0:
                        logger.info("Output directory removed successfully.")
                        return True  # Successfully removed
                    else:
                        logger.error(f"Attempt {attempt + 1} failed to remove output directory.")
                else:
                    logger.info("Output directory does not exist.")
                    return True  # No need to remove if it doesn't exist
                time.sleep(delay)
            return False  # Failed to remove after retries

        # Call the function to attempt removing the directory
        if not remove_directory_with_retry(container):
            logger.error("Failed to remove the output directory after multiple attempts.")
            continue  # Skip this iteration or handle it accordingly

        # Step 5: Run the MapReduce job if the directory was removed
        logger.info("Running MapReduce job")

        exec_result = container.exec_run(
            "hadoop jar /tmp/map_reduce.jar org.apache.hadoop.examples.DecisionTreeMapReduce input output",
            demux=True
        )

        # Check if the job started successfully
        if exec_result.exit_code != 0:
            stderr = exec_result[1] if exec_result[1] else 'No error output'  # No decoding needed here
            logger.error(f"MapReduce job failed to start. Error: {stderr}")
        else:
            logger.info(f"MapReduce job started successfully. Logs: {exec_result[0]}")


        # Step 6: Check if the MapReduce job is completed (check for output directory in HDFS)
        logger.info("Waiting for MapReduce job to finish...")
        job_complete = False
        while not job_complete:
            check_output = container.exec_run("hdfs dfs -test -e /user/root/output/part-r-00000")
            if check_output.exit_code == 0:
                job_complete = True
                logger.info("MapReduce job completed successfully.")
            else:
                logger.info("MapReduce job not finished, waiting...")
                time.sleep(30)  # Wait for 30 seconds before checking again

        # Step 7: Get the output from HDFS (`part-r-00000`)
        logger.info("Fetching output from HDFS")
        fetch_command = "hdfs dfs -cat /user/root/output/part-r-00000"
        result = container.exec_run(fetch_command)

        if result.exit_code == 0:
            # Step 8: Process the fetched data and insert into MongoDB
            content = result.output.decode("utf-8").strip()
            if content:
                # Insert data into MongoDB with timestamp and hour
                current_timestamp = int(time.time())
                current_hour = datetime.now().strftime("%H")

                document = {
                    "content": content,
                    "timestamp": current_timestamp,
                    "hour": current_hour
                }

                trees_col.insert_one(document)
                logger.info(f"Inserted content into MongoDB, hour: {current_hour}")
            else:
                logger.warning("No content found in the output file.")
        else:
            logger.error(f"Failed to fetch HDFS output: {result.stderr.decode('utf-8')}")

        # Step 9: Wait before the next iteration
        logger.info("Waiting 1 hour. Modify this cooldown in config.py")
        time.sleep(config.COOLDOWN)
