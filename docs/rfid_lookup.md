# RFID Lookup

```shell
curl -H 'application/x-www-form-urlencoded' -d 'rfid=0001234567' "http://192.168.200.32:8080/api/v1/lookupByRfid"
```

## Valid ID Response

```text
> POST /api/v1/lookupByRfid HTTP/1.1
> Host: 192.168.200.32:8080
> User-Agent: curl/7.58.0
> Accept: */*
> Content-Length: 15
> Content-Type: application/x-www-form-urlencoded

< HTTP/1.1 200 OK
< Content-Type: application/json
< Content-Length: 382
```

```json
{
  "status" : {
    "success" : true,
    "message" : "Success!"
  },
  "result" : {
    "user" : {
      "fullName" : "Andrew LeCody",
      "email" : "andrewlecody@gmail.com",
      "phone" : "1234567890",
      "username" : "aceat64",
      "groups" : [ "Voting Members", "Automotive 102 (Lift Training)", "Google Apps Users", "Members" ]
    },
    "accessGranted" : true
  }
}
```

## Invalid ID Response

```text
> POST /api/v1/lookupByRfid HTTP/1.1
> Host: 192.168.200.32:8080
> User-Agent: curl/7.58.0
> Accept: */*
> Content-Length: 15
> Content-Type: application/x-www-form-urlencoded

< HTTP/1.1 200 OK
< Content-Type: application/json
< Content-Length: 119
```

```json
{
  "status" : {
    "success" : true,
    "message" : "Success!"
  },
  "result" : {
    "accessGranted" : false
  }
}
```
