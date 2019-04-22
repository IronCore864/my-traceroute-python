# Description

Doing a "traceroute" to a destination host, output the path, and find the slowest host.

Since traceroute is not heavily depending on performance (networking time is the most cost), I choose Python for quicker implementation than golang.

I did not fully implement the checksum part myself but referred to some articles and algorithms. I think there might be a better library to do checksum in python but I didn't find a good one in a short time.

# Dependency

- python (2 and 3 both works)
- root (SUID won't work for scripts; without root permission there will be an error message "You need to be root to run this program!")
- pytest

Run:

```
pip3 install -r requirements.txt
```

# Run

Example:

```
sudo python3 mytraceroute.py www.google.com
```

# Test

```
sudo python3 -m pytest --capture=sys
```
# References
- [ICMP](https://en.wikipedia.org/wiki/Internet_Control_Message_Protocol)
- [Internet Control Message Protocol (ICMP) Parameters](https://www.iana.org/assignments/icmp-parameters/icmp-parameters.xhtml#icmp-parameters-codes-0)
- [Internet Checksum specified in RFC 1071](https://osqa-ask.wireshark.org/questions/11061/icmp-checksum)
- [in_cksum in iputils](https://github.com/iputils/iputils/blob/master/ping.c#L1103)
- [An Article on Internet Checksum](https://www.jianshu.com/p/1e4805c62415)
- [An Implementation of Checksum](https://github.com/pferate/python_ping/blob/master/ping.py#L265)
