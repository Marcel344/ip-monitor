# ip-monitor

<img width="516" alt="Screen Shot 2020-07-05 at 5 33 18 PM" src="https://user-images.githubusercontent.com/33400226/86535488-5ae78080-bee9-11ea-91f4-c5a7f98ab42c.png">


A simple straight forward script with a simple UI that allows you monitor the status of multiple IP addresses at once, very useful if you want to check your connection to printers
and other devices connected via network, it can also be used to check status of public domains such as Google, facebook etc ... This program spawns a thread for 
every new ip added and stores all of them in the "devices" folder that is automatically created, if the folder is already created then the program will load all 
IPs from there. 


## Installation 

pip3 install -r Requirements.txt

python3 main.py
