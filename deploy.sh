#!/usr/bin/env bash

rm -rf ./.chalice/config.json
sed "s/##BOT_TOKEN##/$(cat TOKEN)/" ./config.json.raw > ./.chalice/config.json
chalice deploy

