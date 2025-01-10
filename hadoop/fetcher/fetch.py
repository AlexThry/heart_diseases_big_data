import config
import pymongo
import time
import os
from datetime import datetime, timedelta




if __name__ == "__main__":
    while True:
        myclient = pymongo.MongoClient(config.MONGO_URL)
        mydb = myclient[config.DB_NAME]

        patient_col = mydb["patients"]
        
        one_hour_ago = int(time.time()) - 3600
        recent_patients = patient_col.find({"time": {"$gte": one_hour_ago}})
        recent_patients_list = list(recent_patients)
        
        output_dir = datetime.now().strftime("./output/")
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, "patients.txt")

        with open(output_file, "w") as f:
            for patient in recent_patients_list:
                f.write(str(patient) + "\n")
                
        os.system(f"docker cp {output_file} namenode:/tmp")
        
        os.system(f"docker exec namenode hdfs dfs -mkdir -p /user/root/input")
        os.system(f"docker exec namenode hdfs dfs -test -d /user/root || docker exec namenode hdfs dfs -mkdir -p /user/root")
        os.system(f"docker exec namenode hdfs dfs -put /tmp/{os.path.basename(output_file)} /user/root/input/")
        
        time.sleep(config.COOLDOWN)
