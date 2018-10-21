#!/bin/bash

LINES_TO_GEN=20

if [[ ! -z "${1}" ]]
then
  LINES_TO_GEN="${1}"
fi

#docker run --rm python:2-alpine /bin/ash -c 'apk add --no-cache git ; git clone https://github.com/kiritbasu/Fake-Apache-Log-Generator.git ; cd Fake-Apache-Log-Generator ; pip install numpy ; pip install pytz ; pip install -r requirements.txt ; python apache-fake-log-gen.py -n 20'

#docker run --rm python:2-alpine /bin/ash -c 'apk add --no-cache gcc git ; git clone https://github.com/kiritbasu/Fake-Apache-Log-Generator.git ; cd Fake-Apache-Log-Generator ; pip install --upgrade pip ; pip install -r requirements.txt ; python apache-fake-log-gen.py -n 20'

#docker run --rm python:3-alpine /bin/ash -c 'apk add --no-cache --update python python-dev gfortran py-pip build-base gcc git py-numpy ; git clone https://github.com/kiritbasu/Fake-Apache-Log-Generator.git ; cd Fake-Apache-Log-Generator ; pip install --upgrade pip ; pip install pytz ; pip install -r requirements.txt ; python apache-fake-log-gen.py -n 20'

# includes parts of https://stackoverflow.com/a/33424723
#docker run --rm python:2-alpine /bin/ash -c 'apk add --no-cache --update python python-dev gfortran py-pip build-base gcc git py-numpy ; git clone https://github.com/kiritbasu/Fake-Apache-Log-Generator.git ; cd Fake-Apache-Log-Generator ; pip install --upgrade pip ; pip install pytz ; pip install -r requirements.txt ; python apache-fake-log-gen.py -n 20'

docker run --rm python:2.7.15-stretch /bin/bash -c "apt-get install -y git &>/dev/null ; git clone https://github.com/kiritbasu/Fake-Apache-Log-Generator.git &>/dev/null ; cd Fake-Apache-Log-Generator ; pip install -r requirements.txt &>/dev/null ; python apache-fake-log-gen.py -n ${LINES_TO_GEN}"

# this works too, as an alternative
#docker run --rm mingrammer/flog -n ${LINES_TO_GEN}