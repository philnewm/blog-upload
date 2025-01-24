---
tags:
  - ansible
  - molecule
  - automation
  - blog
---
# Getting started with Ansible Molecule

## Intro

---

After reading through a bunch of Ansible molecule setup guides I noticed quite a bunch of them were outdated in at least one critical aspect. Will discuss the details of this in [Prepare development environment](#prepare-development-environment).
@@TODO make inline markdown style links work in obsidian.

So this is a guide on setting up Ansible Molecule for testing Ansible roles by running them against virtual machines. These virtual machines will be controlled by Vagrant using VirtualBox as provider.
The code in this guide was developed and tested on AlmaLinux9 and Ubuntu22.04 for the software versions mentioned in [Requirements](#requirements)

@@TODO figure out rules for separator placement

## Requirements

---

### System

Since we will use VirtualBox virtual Machines in this guide it's required for you system to have virtualization enabled in your Mainboards BIOS or UEFI.
Check this [article](https://helpdeskgeek.com/how-to/how-to-enable-virtualization-in-bios-for-intel-and-amd/) for further details

This guide is intended to be followed on a Linux system.
This articles assumes you got a basic understanding of Ansible and how to operate within the Linux terminal.
To follow this [guide on a Windows system](https://ultahost.com/knowledge-base/install-ansible-on-windows/) you will need to use the Windows Subsystem for Linux (WSL) since Ansible is not supported on Windows.
It does however support remote controlling [Windows hosts](https://docs.ansible.com/ansible/latest/os_guide/intro_windows.html).

### Python

You will need python >= 3.10 to install the latest versions of all required python packages.
Additional the python-venv and python-pip package will be required.
Here just the example install command for Ubuntu22.04
`sudo apt-get install python3.12 python3.12-venv python3-pip`

> [!tip] Creating a [python virtual environment](https://realpython.com/python-virtual-environments-a-primer/) for Ansible first is highly recommended.

```reference
title: "Create virtual environment"
file: ./.github/workflows/ansible_molecule_getting_started_ci.yml
start: 38
end: "+1"
language: shell
fold: true
ln: true
```

Next we need a bunch of python packages like Ansible, Molecule and its Vagrant plugin.

Create a project directory and `cd` into it.
Create a `requirements.txt` file containing these lines:

```reference
title: "requirements.txt"
file: ./ansible/molecule_getting_started/resources/requirements.txt
language: shell
fold: true
ln: true
```

> [!tip]- docker python packages
> Installing the docker python package is only necessary due to a bug [#32540](https://github.com/ansible/molecule/issues/2540) in molecule plugins.
> A fix for this one is already merged, see [#166](https://github.com/ansible-community/molecule-plugins/issues/166) but no new release happened so far.

Now you can run upgrade pip (just to be sure) and install the requirements.

```reference
title: "Install requirements"
file: ./.github/workflows/ansible_molecule_getting_started_ci.yml
start: 53
end: "+1"
language: shell
fold: true
ln: true
```

### Tools

As the title suggests you also need Virtualbox and Vagrant installed to follow along.

**Vagrant** is a virtual machine management tool which allows molecule to create, start and remove virtual machines in an automated way.
**VirtualBox** on the other hand is the virtualization provider and handles all the heavy lifting when it comes to virtualizing your hardware.
See the following table for download pages and version used for the following examples.

| Tool       | Download Page                                                       | Version used here |
| ---------- | ------------------------------------------------------------------- | ----------------- |
| Virtualbox | [Installers](https://www.virtualbox.org/wiki/Downloads)             | 7.1.4             |
| Vagrant    | [Install commands](https://developer.hashicorp.com/vagrant/install) | 2.4.3             |

```reference
title: "Install vagrant on debian-based systems"
file: ./.github/workflows/ansible_molecule_getting_started_ci.yml
start: 73
end: "+3"
language: shell
fold: true
ln: true
```

It seems like the install command on the VirtualBox website for RedHat based system got a typo in it - at least I needed to change it to the one below to make it work.

~~~tabs
---tab apt-get
```bash linenums="1" title="Install on Debian-based systems"
sudo sh -c 'echo "deb [arch=amd64 signed-by=/usr/share/keyrings/oracle-virtualbox-2016.gpg] https://download.virtualbox.org/virtualbox/debian $(lsb_release -sc) contrib" >> /etc/apt/sources.list'
wget -O- https://www.virtualbox.org/download/oracle_vbox_2016.asc | sudo gpg --yes --output /usr/share/keyrings/oracle-virtualbox-2016.gpg --dearmor
sudo apt-get update
sudo apt-get install virtualbox-7.1 -y
```
---tab dnf
```bash linenums="1" title="Install on RedHat-based systems"
wget -q https://www.virtualbox.org/download/oracle_vbox_2016.asc -O- | rpm --import oracle_vbox_2016.asc
sudo dnf update
sudo dnf install virtualbox-7.1 -y
```
~~~

Verify the successful installation of both tools by checking their version.

```bash linenums="1"
VBoxManage --version
vagrant --version
```

## Prepare development environment

---

While I was trying to understand molecule I came across many guides mentioning the command `molecule role init`.
This one doesn't exist anymore since version [6.0.0](https://github.com/ansible/molecule/releases/tag/v6.0.0) - it was removed intentional to get rid of the [Ansible-Galaxy](https://github.com/ansible/galaxy) dependency. By now you simply use the `role init` command to initialize an Ansible role and initialize a molecule scenario from within the role afterwards.

```reference
title: "Setup role and molecule scenario"
file: ./.github/workflows/ansible_molecule_getting_started_ci.yml
start: 84
end: "+2"
language: shell
fold: true
ln: true
```

For now we'll just go with the *default* scenario to keep it simple.
Now you got a "molecule" directory inside the role containing a bunch of default .yml files.

```code title="Role Structure"
📦sample_role
 ┣ 📂defaults
 ┃ ┗ 📜main.yml
 ┣ 📂files
 ┣ 📂handlers
 ┃ ┗ 📜main.yml
 ┣ 📂meta
 ┃ ┗ 📜main.yml
 ┣ 📂molecule
 ┃ ┗ 📂default
 ┃   ┣ 📜converge.yml
 ┃   ┣ 📜create.yml
 ┃   ┣ 📜destroy.yml
 ┃   ┗ 📜molecule.yml
 ┣ 📂tasks
 ┃ ┗ 📜main.yml
 ┣ 📂templates
 ┣ 📂tests
 ┃ ┣ 📜inventory
 ┃ ┗ 📜test.yml
 ┣ 📂vars
 ┃ ┗ 📜main.yml
 ┗ 📜README.md
```

For details about how each file and directory inside this role structure is supposed to be used see the [Ansible documentation](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_reuse_roles.html#role-directory-structure)

## Instance Creation

---

### Default Instance

Creating a molecule instance is done by running `molecule create` if you do that right away from the roles root directory you will most likely encounter the following error:

```code
ERROR    Computed fully qualified role name of sample does not follow current galaxy requirements.
Please edit meta/main.yml and assure we can correctly determine full role name:

galaxy_info:
role_name: my_name  # if absent directory name hosting role is used instead
namespace: my_galaxy_namespace  # if absent, author is used instead
```

This happens due to molecule running a [role name-check](https://ansible.readthedocs.io/projects/molecule/configuration/#role-name-check) by default.
As stated in the documentation you can either disable the check or just add the `role_name` and `namespace` to the `meta/main.yml` file.

Now running `molecule create` should, while throwing a bunch of warnings, already work.
Running `molecule list` should now show this table.

| Instance Name | Driver Name | Provisioner Name | Scenario Name | Created | Converged |
| ------------- | ----------- | ---------------- | ------------- | ------- | --------- |
| instance      | default     | ansible          | default       | true    | false     |

This will create a default instance using the [delegated driver](https://ansible.readthedocs.io/projects/molecule/configuration/#delegated), which is just called "default".
As the title suggests we will use Vagrant as driver with VirtualBox as a provider in this example.
So run `molecule destroy` to remove that default instance again.
If you run `molecule drivers` you should see a list of installed drivers including `vagrant`.
Take a look at the [molecule-plugins repository](https://github.com/ansible-community/molecule-plugins/blob/main/README.md) for additional information

### Cleaning up

Molecule stores all instance related data in a so called *ephermal directory* and removes it when running `molecule reset`.
It's placed at `~/.cache/molecule/<role-name>/<scenario-name>` by default and usually gets displayed during instance creation @@TODO check instance creation output. 
Running `molecule reset` might result in a python-traceback related to docker on RHEL-systems but will still work and remove the directory as expected.

> [!warning]- Python traceback explanation for `molecule reset`
> Indicates docker and or the python module isn't installed on your system, see [#166](https://github.com/ansible-community/molecule-plugins/issues/166)
> Happens e.g. on Almalinux 9 due to podman being the default container service instead of docker and molecule doesn't seem to like this.

### Vagrant Instance

```reference
title: "molecule.yml"
file: ./ansible/molecule_getting_started/resources/molecule.yml
language: yaml
fold: true
ln: true
```

You can find some explanation of all these settings in the [Ansible molecule docs](https://ansible.readthedocs.io/projects/molecule/getting-started/#inspecting-the-moleculeyml)
> [!info]- VirtualBox Network Setup
> Assigning a network-interface using a `192.168.56.X` address is crucial here.
> VirtualBox sets up two virtual networks  by default.
>
> * vboxnet0 - which is Host-only using 192.168.56.1
> * NatNetwork - using 10.0.2.X
>
> NatNetwork will be used by default but requires port forwarding from the host to the VM to make it accessible from e.g. a browser on the host
> To get around this we just assign a static address from the host-only network.
>

```reference
title: "Initialize vagrant scenario"
file: ./.github/workflows/ansible_molecule_getting_started_ci.yml
start: 144
end: "+6"
language: shell
fold: true
ln: true
```

@@ TODO research line number referencing in Ansible books
Line 1: Initialize a new scenario using explicit parameters to use vagrant
Line 2: The default `create.yml` file will cause connection issues on start-up so we fix this by copying the one from the molecule vagrant plugin itself
Line 3: The default `destroy.yml`file won't destroy the vagrant box itself so we replace it by copying the one from the molecule vagrant plugin itself
Line 4: @@TODO try to get rid of this line - requires removing debug formatting from molecule.yml
Line 5: Now replace the molecule config file `molecule/default/molecule.yml` with the provided one which uses AlmaLinux9. - Get other vagrant boxes on [vagrant cloud](https://portal.cloud.hashicorp.com/vagrant/discover/almalinux/9)
Line 6: Same goes for the `converge.yml` playbook
Line 7: Same goes for the `verify.yml` playbook

Running `molecule create` and `molecule list` when it's done should now display a vagrant instance.

### Access Vagrant Instance

Accessing an instance is supposed to be done by running `molecule login`, this is currently not working due to a [bug](https://github.com/ansible-community/molecule-plugins/issues/239) and should be resolved with the next release.
In the meantime you can run `vagrant global-status` to get the vagrant instance IDs and `vagrant ssh <id>` to log into one of the VMs displayed. Afterwards just type `exit` to drop out of the instance again.

## Provision a service

---

After setting up this vagrant instance successfully it is now time to make it do something using Ansible as its provisioner. We will use these tasks so set up an Apache web-server.
This is just a very basic example for demonstration.

```reference
title: "tasks.yml"
file: ./ansible/molecule_getting_started/resources/tasks.yml
language: yaml
fold: true
ln: true
```

Now replace the content of `tasks/main.yml` with these yaml tasks.

Next run `molecule converge` to run these tasks against the VirtualBox VM.
After this ran successfully you should be able to just copy the IP address displayed by the debug task e.g. `192.168.56.10` to your browser and see the default Apache web-server page right away.

Even tho this is nice, testing the functionality of this web-server manually isn't quite a scalable approach. It's time to set up automated testing for this role.

## Test Vagrant Instance

---

We will use [Ansible for testing](https://ansible.readthedocs.io/projects/molecule/configuration/?h=#molecule.verifier.ansible.Ansible) as well to stay with the default and to keep it simple. Another popular option for molecule testing is [testinfra](https://ansible.readthedocs.io/projects/molecule/configuration/?h=#molecule.verifier.testinfra.Testinfra)
Take a look now at these test tasks which should be self-explanatory due to their names.

```reference
title: "tests.yml"
file: ./ansible/molecule_getting_started/resources/tests.yml
language: yaml
fold: true
ln: true
```

Place these tasks into a file called `tests.yml` in the tasks directory to make them easily accessible.
Now you should be able to run `molecule verify` to have these tests run against the VM.

## Vagrant

Explain what gets saved where and how does the ephemeral directory work

## Wrap-Up

___


