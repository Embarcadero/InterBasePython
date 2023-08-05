import sys
from sphinx.ext import intersphinx

class DummyApp(object):
  srcdir = "."

  def warn(self, msg):
    sys.stderr.write("%s\n" % msg)

def main():
  app = DummyApp()
  # baseurl to use
  uri = ""
  inv = sys.argv[1]
  inventory = intersphinx.fetch_inventory(app, uri, inv)
  for k in inventory.keys():
    print "Type: %s" % k
    for name, value in inventory[k].items():
      print "  %s -> '%s'" % (name, value[2])

  return 0

if __name__ == "__main__":
  sys.exit(main())
