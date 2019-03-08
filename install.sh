#! /bin/bash

# This will be naive install script

if [ -d "$HOME/.update" ];then
    mkdir "$HOME/.update"
fi

# Step 1 
# Copy the code from github
#git clone https://github.com/X20435668/cs5331_project.git $HOME/.update

# Step 3
# Update .bashrc or zshrc to add $HOME/.update to the path
FILE_NAME=`echo $SHELL | awk -F '/' '{printf ".%src\n",$NF}'`
echo "$HOME/$FILE_NAME"

contains() {
    string="$1"
    substring="$2"
    if test "${string#*$substring}" != "$string"
    then
        return 1    # $substring is in $string
    else
        return 0    # $substring is not in $string
    fi
}

contains "$PATH" "$HOME/.update/bin"

if [ $? -eq 0 ];then
    echo "Not contains \"$PATH\" \"$HOME/.update/bin\""
    echo "export PATH=\"\$HOME/.update/bin:\$PATH\"\n" >> "$HOME/$FILE_NAME"
fi

echo "PLEASE restart the terminal to let install take effect"
