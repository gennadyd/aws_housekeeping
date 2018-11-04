import boto3
import traceback
import datetime
import re
# import json

timeLimit = (datetime.datetime.now() - datetime.timedelta(days=7)).isoformat()

class AWS_housekeeping():
    def __init__(self):
        # self.access_key = "<access_key_id>"
        # self.secret_key = "<secret_key_id>"
        # self.region = "<region>"
        # self.account = "<12_digit_account_number>"
        # self.ec2_conn = boto3.client('ec2', self.region, aws_access_key_id=self.access_key, aws_secret_access_key=self.secret_key)

        self.account = "self"
        self.region_name = "us-east-1"
        self.ec2_client = boto3.client('ec2',region_name=self.region_name)

    def getVolumes(self):

        self.total_volumes_size = 0
        self.all_volumes = dict()
        self.available_volumes = list()
        self.total_available_volumes_size = 0

        response = self.ec2_client.describe_volumes()
        for data in response["Volumes"]:
            volume_id = data["VolumeId"]
            volume_state = data["State"]
            volume_size = data["Size"]

            if volume_state == "available":
                self.available_volumes.append(volume_id)
                self.total_available_volumes_size += volume_size

            self.total_volumes_size += volume_size

            self.all_volumes[data["SnapshotId"]] = volume_size

        print("Total Volumes Size [%s]TB " % int(self.total_volumes_size/1024))

    def deleteVolumes(self):
        print("Total Unused (available) Volumes Size [%s]TB " % int(self.total_available_volumes_size / 1024))


    def deleteSnapshots(self):
        self.total_snaps = []
        self.snaps_to_delete = []
        self.volumes_to_delete = 0

        response = self.ec2_client.describe_snapshots(OwnerIds=[self.account])
        for data in response["Snapshots"]:
            self.total_snaps.append(data["SnapshotId"])
            snap_description = data["Description"]
            try:
                amiID = re.search('^Created by CreateImage\([^)]+\) for ([^ ]+)', snap_description).group(1)
            except AttributeError:
                amiID = 'unknown'  # apply your error handling

            if amiID != 'unknown' and amiID not in self.total_images:
                snap_created_time = data["StartTime"].isoformat()
                snap_id = data["SnapshotId"]
                if snap_created_time < timeLimit:
                    # if snap_id in self.all_volumes:
                    #     self.volumes_to_delete += self.all_volumes[snap_id]
                    #     print(" volumes_to_delete size ", self.volumes_to_delete)
                    try:
                        self.snaps_to_delete.append(snap_id)
                        # print("Deleting snap_id ",snap_id )
                        #self.ec2_client.delete_snapshot(SnapshotId=snap_id)
                    except:
                        status_message = str(traceback.format_exc())
                        print(status_message)
                        pass

        print("Total Snapshots [%s], Deleted Snapshots [%s]" % (len(self.total_snaps), len(self.snaps_to_delete)))

    def deleteAMIs(self):
        self.total_images = []
        self.images_to_delete = []
        response = self.ec2_client.describe_images(Owners=[self.account])
        for data in response["Images"]:
            image_id = data["ImageId"]
            image_created_time = data["CreationDate"]
            image_name = data["Name"]

            self.total_images.append(image_id)

            if re.search('.*(Lambda).*', image_name):
                if image_created_time < timeLimit:
                    try:
                        self.images_to_delete.append(image_id)
                        #print("Deregestering ", image_id)
                        #self.ec2_client.deregister_image(ImageId=image_id)
                    except:
                        status_message = str(traceback.format_exc())
                        print(status_message)
                        pass

        print("Total AMIs [%s], Deleted AMIs [%s]" % (len(self.total_images), len(self.images_to_delete)))

if __name__ == '__main__':

    aws_obj = AWS_housekeeping()

    aws_obj.getVolumes()
    aws_obj.deleteAMIs()
    aws_obj.deleteSnapshots()
    aws_obj.deleteVolumes()
