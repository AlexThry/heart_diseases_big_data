import config
import pymongo
import time
import os
from datetime import datetime
import logging
import docker
import io
import tarfile

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    client = docker.from_env()

    while True:
        myclient = pymongo.MongoClient(config.MONGO_URL)
        mydb = myclient[config.DB_NAME]

        patient_col = mydb["patients"]
        one_hour_ago = int(time.time()) - 3600
        recent_patients = patient_col.find({"timestamp": {"$gte": one_hour_ago}, "output": {"$exists": True}})
        recent_patients_list = list(recent_patients)

        logger.info(f"Fetched {len(recent_patients_list)} patients from the database.")
                
        output_dir = datetime.now().strftime("./output/")
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, "patients.txt")

        with open(output_file, "w") as f:
            for patient in recent_patients_list:
                patient.pop("_id", None)
                patient.pop("timestamp", None)
                f.write(str(patient).replace("'", '"') + "\n")
                
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

        container.exec_run("hdfs dfs -mkdir -p /user/root/input")
        logger.info(f"Copied patients infos in namenode")

        container.exec_run("hdfs dfs -rm -f /user/root/input/{}".format(os.path.basename(output_file)))
        logger.info("Removed old patients infos from hdfs system")

        container.exec_run("hdfs dfs -put /tmp/{} /user/root/input/".format(os.path.basename(output_file)))
        logger.info("Added new patients infos into hdfs system")

        logger.info("Waiting 1h. Modify this cooldown in config.py")
        time.sleep(config.COOLDOWN)
