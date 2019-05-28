## AWS SES Receiver e-mail forward e-mail other e-mail account

---
[![Build Status](https://travis-ci.org/cesarbruschetta/ses-receive-email-forward.svg?branch=master)](https://travis-ci.org/cesarbruschetta/ses-receive-email-forward)
[![CodeFactor](https://www.codefactor.io/repository/github/cesarbruschetta/ses-receive-email-forward/badge)](https://www.codefactor.io/repository/github/cesarbruschetta/ses-receive-email-forward)
[![Coverage Status](https://coveralls.io/repos/github/cesarbruschetta/ses-receive-email-forward/badge.svg?branch=master)](https://coveralls.io/github/cesarbruschetta/ses-receive-email-forward?branch=master)

[![buddy pipeline](https://app.buddy.works/cesarbruschetta/ses-receive-email-forward/pipelines/pipeline/189554/badge.svg?token=06562eb22b2295e06d5acef2c4d89e84e5cb4e48db9f96daf96dbfbdbe7096a5 "buddy pipeline")](https://app.buddy.works/cesarbruschetta/ses-receive-email-forward/pipelines/pipeline/189554)
---

### Test

Command to run unit tests

```
$ python setup.py test
```

### Configuration

Environment variables for application configuration

* Log Level
```
$ export LOGGER_LEVEL=INFO
```

* Emails to forward
```
$ export FORWARD_ADDRESSES="user1@example.com,user2@example.com"
```

#### Thanks to:

- Dincer Kavraal -- dincer(AT)mctdata.com

#### References

- https://gist.github.com/stenius/c6983f990bbbb1e49e4f
- https://bravokeyl.com/how-to-set-up-email-forwarding-with-amazon-ses/#Create-a-Lambda-function-to-forward-recieved-email
- https://github.com/arithmetric/aws-lambda-ses-forwarder
