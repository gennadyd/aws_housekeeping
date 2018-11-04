# aws_housekeeping
Delete AWS EC2 AMIs, Snapshots and Volumes
AWS do not provide any one click solution to delete the snapshots/AMIs(in bulk) older than certain numbers of days. 
So, I've wrote a simple python script that will erase all the AMIs, snapshots and volumes older than the X days mentioned by the user.
