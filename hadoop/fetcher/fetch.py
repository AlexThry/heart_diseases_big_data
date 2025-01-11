import config
import pymongo
import time
import os
from datetime import datetime, timedelta
import logging




if __name__ == "__main__":
    while True:
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        
        myclient = pymongo.MongoClient(config.MONGO_URL)
        mydb = myclient[config.DB_NAME]

        patient_col = mydb["patients"]
        
        one_hour_ago = int(time.time()) - 3600
        recent_patients = patient_col.find({"timestamp": {"$gte": one_hour_ago}})
        recent_patients_list = list(recent_patients)        

        logger.info(f"Fetched {len(recent_patients_list)} patients from the database.")
                
        output_dir = datetime.now().strftime("./output/")
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, "patients.txt")

        with open(output_file, "w") as f:
            for patient in recent_patients_list:
                f.write(str(patient) + "\n")
                
        os.system(f"docker cp {output_file} namenode:/tmp")
        
        os.system(f"docker exec namenode hdfs dfs -mkdir -p /user/root/input")
        logger.info(f"Copied patients infos in namenode")
        os.system(f"docker exec namenode hdfs dfs -test -d /user/root || docker exec namenode hdfs dfs -mkdir -p /user/root")
        logger.info("/user/root/input folder exist")
        os.system(f"docker exec namenode hdfs dfs -rm -f /user/root/input/{os.path.basename(output_file)}")
        logger.info("Removed old patients infos from hdfs system")
        os.system(f"docker exec namenode hdfs dfs -put /tmp/{os.path.basename(output_file)} /user/root/input/")
        logger.info("added new patients infos into hdfs system")
        
        time.sleep(config.COOLDOWN)
