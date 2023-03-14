class BTreeNode() :
    def __init__(self, data) :
        self.data = data
        self.right = None
        self.left = None
        
    def __str__(self) :
        if self.left != None:
            print("Left:(", end = "")
            print(self.left, end = "), ")
        if self.right != None :
            print("Right:(", end = "")
            print(self.right, end = "), ")
        return "(Data = " + self.data + ")" 
    
    InPr = {}
    InPr['+'] = "PLUS"
    InPr['?'] = "MAYBE"
    InPr['*'] = "STAR"
    InPr['&'] = "CONCAT"
    InPr['|'] = "UNION"
  
    @staticmethod
    # Function to build Expression Tree
    def buildExpTree(s):
    
        # stack to hold nodes
        stN = []
    
        # stack to hold chars
        stC = []
    
        # priority dictionary to associate a priority to every operator
        pDict = {}
        pDict['&'] = 2
        pDict['|'] = 1
        pDict['*'], pDict["+"], pDict['?'] = 3,3,3
        pDict['('] = 0
        pDict[')'] = 0
            
        i = 0            
        while i < len(s):
            if s[i] == '(':
                # first we verify if there is a concatentaion
                if i > 1 :
                    if s[i - 1] not in "(|&" :
                        s = s[:i] + '&' + s[i:]
                        print(s)
                        continue # we go back at the '&' character inserted for concatenation
                # otherwise we append the '(' in the character stack
                stC.append(s[i])
                
                        
            # we have an operand
            elif (s[i] not in pDict):
                # possible concat
                if i > 1 :
                    if s[i - 1] not in "(|&" :
                        s = s[:i] + '&' + s[i:]
                        #print(s)
                        continue
                # otherwise we create the node of the operand and push it in the nodes stack
                t = BTreeNode(s[i])
                stN.append(t)
                
            elif pDict[s[i]] > 0:
            
                # verify if the operator has lower priority than the one at the top of the stack
                while (stC and stC[-1] != '(' and ((s[i] != '*' and pDict[stC[-1]] > pDict[s[i]])
                        or (s[i] == '*' and
                        pDict[stC[-1]] == pDict[s[i]]))):
                
                    # get the new node to complete
                    t = BTreeNode(stC[-1])
                    op = stC.pop()
    
                    # get the right child
                    # it's None for *, + and ? operators
                    t1 = None
                    if stN and op not in "*+?":
                        t1 = stN[-1]
                        stN.pop()
    
                    # get the left child
                    t2 = None
                    if stN :
                        t2 = stN[-1]
                        stN.pop()
    
                    # update the tree
                    t.left = t2
                    t.right = t1
    
                    # push the new node to the node stack
                    stN.append(t)
    
                # push the current operator to the char stack
                stC.append(s[i])
                
            elif (s[i] == ')'):
                while (len(stC) != 0 and stC[-1] != '('):
                    
                    # get the new node to complete
                    t = BTreeNode(stC[-1])
                    op = stC.pop()

                    # get the right child
                    # it's None for *, + and ? operators                  
                    t1 = None
                    if stN and op not in "*+?":
                        t1 = stN[-1]
                        stN.pop()
                    
                    # get the left child
                    t2 = None
                    if stN :
                        t2 = stN[-1]
                        stN.pop()
                    
                    # update the tree
                    t.left = t2
                    t.right = t1
                    stN.append(t)
                    
                stC.pop()
            i += 1
        t = stN[-1]
        return t
    
    # we get the prenex by getting the preorder traversal of the tree
    @staticmethod
    def preorder(root) :
        if root == None :
            return ""
        if root.data in BTreeNode.InPr :
            return BTreeNode.InPr[root.data] + " " + BTreeNode.preorder(root.left) + BTreeNode.preorder(root.right)
        return root.data + " " + BTreeNode.preorder(root.left) + BTreeNode.preorder(root.right)
        