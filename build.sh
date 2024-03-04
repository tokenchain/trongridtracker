#!/usr/bin/env bash
. ./update
VERSION_OLD=$(cat version)
pub_ver
VERSION=$(cat version)

REMOTE_HOST=96.8.121.72
REMOTE_DIR=/home/dockerimages/
REMOTE_ROOT=/root/
HUB_NAME=adriansteward
DOCKER_HUB_IMAGE1=$HUB_NAME/chainanalysis:$VERSION
ACCESS_CODE=dckr_pat_mnP-dt76S0CQm-eO8uYwBj6hSzk
DOCKER_FILE=DockerTrackerFactory

login() {
  docker login $HUB_NAME a5ynyDMK731u
}
dcleanup() {
  docker rmi $(docker images -q)
}
get_last_id_wit_name() {
  docker images --format="{{.Repository}} {{.ID}}" | grep "^$1 " | cut -d' ' -f2 | xargs docker rmi
}
get_last_id() {
  docker images -q --no-trunc | sort -r | head -n 1
}
remote_code() {
  # docker login -u acostarata -p dckr_pat_H7WSmNRMK_3vHhszMxfWBODhKms docker.io
  # docker login -u adriansteward -p a5ynyDMK731u docker.io
  # docker login adriansteward a5ynyDMK731u
  docker login -u $HUB_NAME -p $ACCESS_CODE docker.io
}
ssh_docker_upgrade() {
  # linux
  # sed -i "s/1.1.1056/1.1.1057/" "docker-compose.yml"
  # sed -i "" "s/1.1.1056/1.1.1057/" "docker-compose.yml"
  if [ "$VERSION_OLD" != "$VERSION" ]; then
    sed -i "" "s/$VERSION_OLD/$VERSION/" "docker-compose.yml"
  fi
  scp -i ~/.ssh/id_rsa docker-compose.yml root@$REMOTE_HOST:$REMOTE_ROOT
  cat upgrade.sh | ssh -i ~/.ssh/id_rsa root@$REMOTE_HOST /bin/bash
}
localbuildonly() {
  docker build -t $DOCKER_HUB_IMAGE1 -f $DOCKER_FILE .
  echo "$DOCKER_HUB_IMAGE1"
  # docker push adriansteward/skygatenft:1.1.1001
  docker push $DOCKER_HUB_IMAGE1
}
cleanup() {
  rm -rf dist
  rm main_exe.py
}
regulate_compile() {
  dcleanup
  login
  # in the remove docker
  # docker load --input verse_gapminder.tar
  ssh_docker_upgrade
}

package_source_to_zip_01() {
  obsbuidl lib.py 3
  rm lvl2.py
  rm llmziprainbow.zip
  zip llmziprainbow.zip keys_skygate.xlsx lib_obfs.py main.py README.md requirements.txt ./cache/*
}
package_source_to_zip_02() {
  obsmain
  rm llmziprainbow.zip
  zip llmziprainbow.zip main_exe.py README.md requirements.txt ./cache/* ./dist/*
  cleanup
  git_update
}
build_docker_to_hub_docker() {
  obsmain
  login
  localbuildonly
  cleanup
  # git_update
}
check_need_cmd
build_docker_to_hub_docker
