## (5DB) Nexora Data Limited Resource SOD Tool

This tool is Designed specificaly towards resource creators by the Team @ Nexora Data Limited. 

This read me will go over everything that you will need to have this in a fully functioning mannor. 

---

Python Packages 

To run this script you will need to run the following command in you're cmd (Please make sure you have installed Python3+)

pip install pandas

or 

python3 install pandas

---

Getting the server's .json files

You can get these directly from the server list

---

Getting & Uploading you're customers.csv

To get this file you need to request it from Tebex this can be done from ; https://creator.tebex.io/payments (This dose not require permium)

Once you have requested this file and downloaded it you will then check it and make sure that it looks like all the customers. You will then upload it to the Directory named "customers" you do not need to rename this file at all

---

Getting Requirements & Uploading them 

the format is 

ResourceName:PackageID

Resource Name - This is what ever the resource is called when you upload it

PackageID - you can get this form the assett upload

Example of layout

BSD-DriftCounter:123456
BSD-BreathingSimulator:654321

---

Outputs 

When you have finished a full scan it will save the users that do not have the authority to use you're resources inside of the outputs folder. 

You may need to (for saftey purpouses) Have to check this against the  Portals licenses system as it will not pickup users that have been transferd assetts.