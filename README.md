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
