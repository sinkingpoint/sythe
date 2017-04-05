# Sythe

[![Build Status](https://travis-ci.org/sinkingpoint/sythe.svg?branch=master)](https://travis-ci.org/sinkingpoint/sythe)

[![Coverage Status](https://coveralls.io/repos/github/sinkingpoint/sythe/badge.svg?branch=master)](https://coveralls.io/github/sinkingpoint/sythe?branch=master)

Sythe is a rules engine for AWS resources, not unlike [Janitor Monkey](https://github.com/Netflix/SimianArmy/) by
Netflix, or [Cloud Custodian](https://github.com/capitalone/cloud-custodian) by Capital One.

Sythe provides a Domain Specific Language in which rules are defined. This DSL is interpretted at run time
by Sythe. This gives a distinct advantage over the above two offerings - we maintain most of the expressiveness
of Janitor Monkey, in which rules are written in Java and compiled, while also maintaining the ease of deployment
offered by Cloud Custodian (in which configurations are in YAML).

## DSL

A rule in Sythe is defined as follows:

```
<Resource Type>(<Condition>){
    <Action>
    <Action>
}
```

for example the following rule will find all ec2 instances that are in a suspended state
and mark them for deletion in 3 days. It will also send an email to the email address
in the "owner" tag on the resource:

```
ec2_instance(State.Name = "suspended"){
    mark_for_deletion(after: "3 days")
    notify(transport: "ses", to: tag:owner, from: "sythe@company.com")
}
```

Assuming this is put in a file called "rule.sr", this can be run by simply calling
`sythe rule.sr`.
