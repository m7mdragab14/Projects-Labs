1- create users 
useradd -u 1600 -m -s /bin/bash ali
useradd -u 1600 -m -s /bin/bash ahmed
useradd -u 1600 -m -s /bin/bash nour
useradd -u 1600 -m -s /bin/bash sara
useradd -u 1600 -m -s /bin/bash noura

passwd ali
passwd ahmed
passwd nour
passwd sara
passwd noura


2- add users to groups
groupadd developers
groupadd admins

for user in ali ahmed nour sara;do 
  usermod -aG developers $user
  done

usermod -aG admins sara
usermod -aG admins noura


3- setting sudo for a specific group
sudo visudo
  %admins ALL=(ALL) ALL


4- setting password policy by using chage 
for user in ali ahmed nour sara nour;do
  chage -M 90 -m 7 -W 14 $user
  done

- show policy 
chage -l ali 


5- delete a user while keeping their files
userdel ali 
sudo ls -l /home/ali
