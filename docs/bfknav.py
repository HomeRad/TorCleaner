import sys, os
from cStringIO import StringIO

class Node (object):

    def __init__ (self, name, order, filename):
        self.name = name
        self.order = order
        self.filename = filename
        self.level = 0
        self.children = []
        self.sibling_right = None
        self.active = False
        self.parent = None


    def get_url (self, level):
        return "../"*level + self.filename


    def addChildren (self, nodes):
        for node in nodes:
            node.parent = self
            node.level = self.level + 1
            self.children.append(node)


    def write_nav (self, fp, active):
        """write node navigation"""
        descend = has_node(active, self.children)
        if self.active or descend:
            self.write_active(fp)
        else:
            self.write_inactive(fp, active.level)
        if self.sibling_right:
            self.sibling_right.write_nav(fp, active)
        if descend:
            # go to next level
            self.write_nextlevel(fp)
            self.children[0].write_nav(fp, active)


    def write_inactive (self, fp, level):
        fp.write('<a href="%s">%s</a>\n'%(self.get_url(level), self.name))


    def write_active (self, fp):
        fp.write("%s\n"%self.name)


    def write_nextlevel (self, fp):
        fp.write('<br>\n')


    def new_node (self):
        return Node(self.name, sys.maxint, self.filename)


    def __repr__ (self):
        return "<Node %r>"%self.name


    def __lt__(self, other):
        return self.order < other.order


    def __le__(self, other):
        return self.order <= other.order


    def __eq__(self, other):
        return self.order == other.order


    def __ne__(self, other):
        return self.order != other.order


    def __gt__(self, other):
        return self.order > other.order


    def __ge__(self, other):
        return self.order >= other.order


def parse_navtree (dirname):
    nodes = []
    files = os.listdir(dirname)
    for f in files:
        filename = os.path.join(dirname, f)
        htmlname = os.path.join(dirname, os.path.splitext(f)[0]+".html")
        if os.path.isfile(filename) and f.endswith('.nav'):
            flocals = {}
            execfile(filename, {}, flocals)
            nodes.append(Node(flocals['name'], flocals['order'], htmlname))
        elif os.path.isdir(filename):
            subnodes = parse_navtree(filename)
            if subnodes:
                n = subnodes[0].new_node()
                n.addChildren(subnodes)
                nodes.append(n)
    nodes.sort()
    for i,n in enumerate(nodes):
        if (i+1)<len(nodes):
            n.sibling_right = nodes[i+1]
    #print_nodes(nodes)
    return nodes


def print_nodes (nodes):
    for node in nodes:
        print " "*node.level+node.name
        if node.children:
            print_nodes(node.children)


def has_node (node, nodes):
    for n in nodes:
        if node.filename == n.filename:
            return True
        if has_node(node, n.children):
            return True
    return False


def generate_nav (start, nodes):
    for node in nodes:
        print node.filename
        if node.children:
            generate_nav(start, node.children)
        else:
            node.active = True
            fp = StringIO()
            start.write_nav(fp, node)
            nav = '<div class="navigation">\n%s\n</div>' % fp.getvalue()
            node.active = False
            f = file(node.filename)
            data = f.read()
            f.close()
            data = data.replace("<bfk:navigation/>", nav)
            f = file(node.filename, 'w')
            f.write(data)
            f.close()


if __name__=='__main__':
    nodes = parse_navtree(".")
    if nodes:
        generate_nav(nodes[0], nodes)
