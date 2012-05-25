## WHAT

Commis is a [Django](http://djangoproject.com) implementation of [Chef
Server](http://wiki.opscode.com/display/chef/Chef+Server). It's currently
compatible with Django 1.2 through 1.4, and thus has the same dependencies as
those releases:

* Python 2.5 or newer
* A relational database engine (this includes the ships-with-Python SQLite)

On top of that, Commis requires a handful of other pure-Python libraries, such
as PyChef, Celery and PyParsing.


## WHY

There are a number of reasons you may want to deploy Commis instead of the
standard Chef Server implementation or using Opscode's hosted service:

### Simpler deployment

**Chef Server requires many components & runtimes in addition to Ruby**:
RabbitMQ (and thus Erlang), CouchDB (also Erlang), Solr (Java), and `gecode`.
Installation quickly gets complicated on non-Ubuntu platforms such as CentOS or
Fedora (have fun finding up to date `gecode` RPMs or waiting an hour for it to
compile!).  Managing and supporting the different components is also a large
hurdle for users who just want to get started, regardless of platform.

Conversely, in its most basic form, **Commis relies purely upon Python
libraries** -- the embedded SQLite for databasing, Whoosh for text indexing,
and Celery for queuing (which can function without an actual queue when not
needed.)

Furthermore, **you can easily replace these components when necessary, and with
whatever backends you want**.  SQLite crumbles with more than a few concurrent
users? Use Postgres or MySQL (or Oracle or ...). Need non-eager background
jobs? Use any [Celery](http://celeryproject.org/)-supported backend (like
Redis), you're not limited to RabbitMQ. Ditto for text indexing -- anything
[Haystack](http://haystacksearch.org/) supports is fair game.

### Improved hackability

As a third party solution, Commis is free to innovate and add experimental
features that aren't suitable for the official Chef Server project. This
includes things like major UI changes for the web interface and flexible policy
backends that are designed be be altered to suit your needs.

For example, not everybody is able or willing to treat their Chef Server as the
single source of truth -- imagine being able to plug-in or sync your
pre-existing LDAP server or Clusto database such that your Chef recipes see the
data as regular attributes, or even as dynamically managed node or client
entries. And this is just one example.

### Python interoperability

Mostly a sub-case of the above -- Commis, being Python, is a great fit for
shops with pre-existing Python systems or Python deployment experience.
Learning Ruby to write Chef manifests is one thing; becoming comfortable
deploying a complex Ruby web-app is another entirely. With Commis, you might
not have to.


## HOW

Here's how to get started hacking on or evaluating Commis. It assumes you want
to run off the abovementioned pure-Python default stack; to move away from
those defaults, you'll just need to install the additional components you want
and modify `commis/settings.py` appropriately.

### Installation

On the system acting as Chef Server, get Commis installed and running:

* Get Commis: `git clone`, download tarball, etc.
* (Optional but strongly recommended) Create a
  [virtualenv](http://www.virtualenv.org) and activate it.
* Get dependencies: `pip install -r requirements.txt`
* Put Commis on your PYTHONPATH (some settings files need to import
  `commis.<x>`): `pip install -e .`
* Install DB schema: `python commis/manage.py syncdb`
    * By default, this creates a SQLite DB in `commis/commis.db`. You can
    select a different SQL DB in `commis/settings.py`.
    * It will prompt you for a new admin user which you'll use to admin the Web
    UI.
* Start it up to make sure things work: `python commis/manage.py runserver
  0.0.0.0:8000`
    * You may alter the port number to taste.
    * Chef Server runs the Web UI and the API on separate ports; Commis runs
    both on a single port, exposing the API at `/api/*`.
* Hit up `http://<hostname>:8000/`and make sure you can log
  in as your admin user and click around.

### Client/key management

You now have a working Commis install, but you need to do some Chef client/key
management in order for Chef-managed systems, or CLI management tools
(`knife`), to connect. Here's a conceptual overview:

* Chef "clients" are entities that connect to the Chef server API and
  manipulate/query its DB. They are distinct from the Django website user
  accounts (such as your admin user.)
* Clients are really just an association between a name and an RSA key pair
  (think SSH keys -- two chunks of text, one public and one private) 
  stored in the DB along with authorization metadata (admin ability, etc.)
* There are three kinds of clients:
    * **Admin** clients have full privileges, analogous to SQL database root
    users. They grant actual humans access to the Chef server, typically via
    the `knife` CLI tool.
    * **Node** clients represent a Chef-managed system or "node", and are
    analogous to non-root SQL users. They only manipulate their related Node
    object and its data.
    * **Validator** clients are used solely to create new node clients on the
    fly.
* Thus, the workflow you need is:
    * Ensure an admin client exists, so you can manage the server via
    `knife` (currently the primary way to manage Chef Server / Commis, barring
    a richer Web UI.)
    * Ensure a validator client exists and that its private key file is in a
    known location.
    * New Chef-managed systems obtain a copy of the validator key (e.g. via
    `scp` or authenticated download) and use it with `chef-client` to create
    new node clients/keys for themselves.
    * They then use those per-node client accounts to run Chef cookbooks.

#### Actual client/key HOWTO

Here's the specifics on getting your new Commis serve ready to work with client
nodes:

* Make an admin client: `python commis/manage.py commis_client --admin
<name>`.
    * Replace `<name>` with your desired client name or username. It could,
    match your Django-level admin account name or local username, but doesn't
    have to.
    * This creates a file in your working directory named `<name>.pem`.
* Make the validator client: `python commis/manage.py commis_client
  --validator`. This generates `validator.pem` in your working directory.
* Copy both `.pem` files somewhere persistent that you will remember, such as
  `~/.chef/` or `/etc/chef/`.
* Select a system to use for managing your Commis server via `knife` -- could
  be the Commis server itself, or your local workstation.
* On that system, install Chef (e.g. `gem install chef`) and copy down the
  `.pem` files you created above. A good location may be `~/.chef/` as that's
  where Knife defaults to storing its config files and so forth.
* Run `knife configure` (note: no `-i` as other tutorials sometimes use.) It'll
  prompt you for the following:
  * The location of the conf file to generate.
  * The Chef Server URL. This is the hostname or IP of your Commis server, plus
  the port and -- **this is a departure from regular Chef Server** -- a
  trailing `/api`.
      * For example, if you are using the Commis system itself as your
      management host, enter `http://localhost:8000/api`.
  * The client name. This is the admin user you made above, i.e. `<name>`.
  * The validator name. This is `chef-validator` by default.
  * The validator key path. Depending on where you moved that to, give the path
  here, e.g. `~/.chef/validator.pem`.
  * A Chef repository path. Leave this blank.
* Phew! That should have created e.g. `~/.chef/knife.rb`.
* Test out `knife`: make sure your runserver is active, and execute `knife
  client list`. It should spit back the two clients you just made, `<name>` and
  `validator`.

### Running cookbooks on your servers

At this point, you've got Commis running and can manage/query it via `knife`.
The next step is to run some cookbooks on a target server/node!

#### Uploading cookbooks

To run cookbooks, they must be in Commis' database: `chef-client`
expects to get all cookbooks/recipes/etc from the server. We'll
use a trivial test cookbook here:

    .
    └── testcookbook
        └── recipes
            └── default.rb

where `default.rb` is simply:

    log "Hello world!"

Get that `testcookbook` directory onto your `knife` system, enter its parent directory, and execute:

    knife cookbook upload -o . testcookbook

You can verify the upload by visiting the Web UI and viewing the Cookbooks tab,
or running `knife cookbook list`.

#### Executing on a new node

We're almost done. Locate or create a system you're comfortable experimenting
on. There's two ways to update it to run against our Commis server, the
automatic way and the hard way.

#### `knife bootstrap`

The easy way is to simply enter your management workstation's home directory,
and run:

    knife bootstrap <hostname> -x <username> --sudo
    
Use the target's hostname, and your SSH login username used to connect to that
system. It should connect, ensure Chef is installed, and handle the certificate
management for you (including copying the validator cert from your
workstation.)

Caveats:

* Due to a bug in Knife, you have to run this command while inside your home
  directory, or wherever you created a `.chef` directory containing `knife.rb`.
  If you run it from your Commis checkout, it will fail.
  * This is **not** true for other Knife commands like `knife node list` --
  only `bootstrap` appears to be affected.
* Depending on your target server's auth settings, you could leave off the `-x
  <username>` if you have root login enabled. However, we strongly recommend
  not doing this, as it's bad security practice.
* Even if your local workstation username is `<username>`, you still have to
  explicitly specify it with `-x`, as `knife` will try to use `root` otherwise.
* If you're giving a non-human-readable hostname, like an IP address, you can
  also give `-N <nodename>` to override the Chef-facing name this client will
  use.

##### Manual

This is basically what `knife bootstrap` is doing for you:

* Copy `validator.pem` to the target system.
* Obtain the necessary parameters to run `chef-client` against your Commis
  server, which can either be used as CLI flags (see `chef-client --help`), or
  go into a `client.rb` config file:
  * Path to `validator.pem`.
  * Path to desired new client key, e.g. `/etc/chef/<hostname>.pem`.
  * Server URI: same as above for Knife,
  `http://<commis-server-hostname>:8000/api`.
* Execute `chef-client` -- it should create a new node client for itself, named
  after your system's hostname, then run an empty run list.

##### Sanity test and run_list update

* Verify that node creation with `knife node list` on your workstation or on
  the Web UI.
* Update this node's run list to include `"testcookbook"`, again either via
  knife (`knife node run_list add <hostname> testcookbook`) or the Web UI's
  edit form.
    * If using the Web UI, drag the "testcookbook" box from the lower left,
    into the right hand side. Then click "Edit Node" to save, and you're done.
* Run `chef-client` on the target node -- it should print out your "Hello
  world!" log entry in the middle of its run.
* If so, you're done! Add more cookbooks, tweak run lists, and go to town.
