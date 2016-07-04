pxe-server Cookbook
=================
This cookbook sets up the series of scripts for setting up OpenStack in the style of the Center for Data Intensive Science.

Requirements
------------

#### packages
- `isc-dhcp-server` - hands out initial IP and hostname
- `tftpd-hpa` - serves PXE images
- `lighttpd` - hosts preseeds and scripts

Attributes
----------

e.g.
#### lighttpd::default
<table>
  <tr>
    <th>Key</th>
    <th>Type</th>
    <th>Description</th>
    <th>Default</th>
  </tr>
  <tr>
    <td><tt>['lighttpd']['bacon']</tt></td>
    <td>Boolean</td>
    <td>whether to include bacon</td>
    <td><tt>true</tt></td>
  </tr>
</table>

Usage
-----
#### pxe-server::default

e.g.
Just include `pxe-server` in your node's `run_list`:

```json
{
  "name":"my_node",
  "run_list": [
    "recipe[pxe-server]"
  ]
}
```

Contributing
------------
Ask Rafael

License and Authors
-------------------
Authors: TODO: List authors

