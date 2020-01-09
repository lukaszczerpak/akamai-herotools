## Overview

This project is part of automated pipeline. Key features:

* read YAML files with endpoint definition and convert to Phased Release policy rule
* validate Phased Release policy JSON
* update Phased Release policy via OPEN API
* activate Phased Release policy on Akamai Staging
* set up individual lab environment (property + policy) 

## Running the scripts

The package consists of five scripts:

* `generate-prc-rules`
* `cloudlet-validate-policy`
* `cloudlet-policy-update`
* `cloudlet-policy-activate`
* `sa2020-setup-lab`

Detailed documentation on how to use it can be found in the lab script.

## Build

```bash
docker build -t lukaszczerpak/herotools:<version> .
docker tag lukaszczerpak/herotools:<version> lukaszczerpak/herotools:latest
docker push lukaszczerpak/herotools
```
