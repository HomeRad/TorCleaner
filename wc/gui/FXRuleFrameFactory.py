from FXRuleFrame import FXRuleFrame
from FXRewriteRuleFrame import FXRewriteRuleFrame
from FXReplacerRuleFrame import FXReplacerRuleFrame
from FXAllowRuleFrame import FXAllowRuleFrame
from FXBlockRuleFrame import FXBlockRuleFrame
from FXHeaderRuleFrame import FXHeaderRuleFrame
from FXImageRuleFrame import FXImageRuleFrame
from FXNocommentsRuleFrame import FXNocommentsRuleFrame
from FXFolderRuleFrame import FXFolderRuleFrame


class FXRuleFrameFactory:
    """Every Rule (see webfilter/Rules.py) has a "fromFactory" function.
       A factory has a function fromXXXRule for every different Rule
       class.
       This particular factory generates windows which display all the
       variables found in a rule.
    """
    def __init__(self, treeframe):
        """Because we store frames in a hierarchical tree, we need
	   a tree treeframe.
	   To distinguish frames we have a unique index for each."""
        self.treeframe = treeframe
        self.index = 0

    def inc_index(self):
        self.index += 1

    def fromRule(self, rule):
        self.inc_index()
        return FXRuleFrame(self.treeframe, rule, self.index)

    def fromRewriteRule(self, rule):
        self.inc_index()
        return FXRewriteRuleFrame(self.treeframe, rule, self.index)

    def fromReplacerRule(self, rule):
        self.inc_index()
        return FXReplacerRuleFrame(self.treeframe, rule, self.index)

    def fromAllowRule(self, rule):
        self.inc_index()
        return FXAllowRuleFrame(self.treeframe, rule, self.index)

    def fromBlockRule(self, rule):
        self.inc_index()
        return FXBlockRuleFrame(self.treeframe, rule, self.index)

    def fromHeaderRule(self, rule):
        self.inc_index()
        return FXHeaderRuleFrame(self.treeframe, rule, self.index)

    def fromImageRule(self, rule):
        self.inc_index()
        return FXImageRuleFrame(self.treeframe, rule, self.index)

    def fromNocommentsRule(self, rule):
        self.inc_index()
        return FXNocommentsRuleFrame(self.treeframe, rule, self.index)

    def fromFolderRule(self, rule):
        self.inc_index()
        return FXFolderRuleFrame(self.treeframe, rule, self.index)


