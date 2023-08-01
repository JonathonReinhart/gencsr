gencsr
======
`gencsr` is a simple tool to generate an x.509 Certificate Signing Request
(CSR).

It is opinionated and supports the most basic common use-case: A website with
one or more DNS names. Anything more complex than that is better handled by
other tools.

Usage
-----
The hostname is always included in the list of DNS names (Subject Alternative
Name).

You can either pass options on the command line:
```console
$ gencsr --hostname example.com --dns-name www.example.com --dns-name login.example.com
```

Or you can use a config file, in which case no other command line options are
allowed (they are not merged). This is equivalent to the previous example.
```toml
hostname = "example.com"
dns_names = [
    "www.example.com",
    "login.example.com",
]
```

```console
$ gencsr --confg example.com.toml
```
