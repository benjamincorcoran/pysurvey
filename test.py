import json
import param 
import panel as pn
import itertools as it
pn.extension()

def tableFactory(definition):
    _tbl = type(f"t_{definition['tableTitle']}",(surveyTable,),{})
    tbl = _tbl()
    tbl.define(**definition)
    
    return tbl

class surveyTable(param.Parameterized):
    
    def define(self, tableTitle, tableDesc, tableLayout, tableParams):                
        self.tableTitle = tableTitle
        self.tableLayout = tableLayout
        self.tableDesc = tableDesc
        self.tableParams = tableParams
        
        for x in it.chain(*self.tableLayout):
            if x in self.tableParams.keys():
                self._add_parameter(x, self.tableParams[x])
            else:
                self._add_parameter(x, param.Integer(0))
                
    def show(self):
        tbl = pn.Column(pn.pane.Markdown(f"## {self.tableTitle}"), pn.pane.Markdown(f'{self.tableDesc}'))
        
        for row in self.tableLayout:
            r = pn.Row()
            for cell in row:
                r.append(self.param[cell])
            tbl.append(r)
        
        return tbl
    
    def iter_parameters(self):
        for key, parameter in self.param.objects().items():
            yield parameter
    
    def save(self):
        return {x[0]:x[1] for x in self.param.get_param_values()}
                
                
class surveyTab(object):
    
    def __init__(self, tabTitle, tabDesc, tables):
        
        self.tabTitle = tabTitle
        self.tabDesc = tabDesc
        self.tables = [tableFactory(table) for table in tables]
    
    def show(self):
        tabLayout = pn.Column()
        tabLayout.append(pn.pane.Markdown(f'{self.tabDesc}'))
        for table in self.tables:
            tabLayout.append(table.show())

        return (f"{self.tabTitle}", tabLayout)
    
    def save(self):
        tab = {}
        for table in self.tables:
            tab[table.tableTitle]=table.save()
        return tab

    def iter_parameters(self):
        for table in self.tables:
            yield from table.iter_parameters()
                
    
class surveyClass(param.Parameterized):
                
    def __init__(self, surveyTitle, surveyDesc, tabs):
        self.surveyTitle = surveyTitle
        self.surveyDesc = surveyDesc

        self.tabs = []
        for definition in tabs:
            self.tabs.append(surveyTab(**definition))
        
        self.saveButton = pn.widgets.Button(name='Save')
        self.saveButton.on_click(self.save)
        self.submitButton = pn.widgets.Button(name='Submit')
        self.submitButton.on_click(self.submit)
        self.revertButton = pn.widgets.Button(name='Revert')
        self.revertButton.on_click(self.revert)
        
                
        self.surveyControl = pn.Row(self.saveButton, self.submitButton, self.revertButton)
    
    def show(self):
        s = pn.Column(self.surveyControl, pn.pane.Markdown(f"# {self.surveyTitle}"), f"{self.surveyDesc}", sizing_mode='stretch_both')
        tabs = pn.Tabs()
        for tab in self.tabs:
            tabs.append(tab.show())
        s.append(tabs)
        return s

    def save(self, event):
        tabs = {}
        for tab in self.tabs:
            tabs[tab.tabTitle]=tab.save()
        
        with open('test.txt', 'w') as f:
            f.write(json.dumps(tabs, indent=4))
    
    def iter_parameters(self):
        for tab in self.tabs:
            yield from tab.iter_parameters()
    
    def submit(self, event):
        for param in self.iter_parameters():
            param.constant=True
    
    def revert(self, event):
        for param in self.iter_parameters():
            param.constant=False


                
                
surveyDefinition = {
    'surveyTitle': 'An Example Survey',
    'surveyDesc': 'A description of the example survey.',
    'tabs': [
        {
            'tabTitle':'Tab 1',
            'tabDesc': 'A description of the tabbed section.',
            'tables': [
                {
                    'tableTitle':'Table 1',
                    'tableDesc':'A description of table 1.',
                    'tableLayout':[['A','B','C'],['D','E','F']],
                    'tableParams':{'A':param.String('A')}
                },
                {
                    'tableTitle':'Table 2',
                    'tableDesc':'A description of table 1.',
                    'tableLayout':[['A'],['J','K','L']],
                    'tableParams':{'A':param.ObjectSelector(default='Asia', objects=['Africa', 'Asia', 'Europe'])}
                }
            ]
        },
        {
            'tabTitle':'Tab 2',
            'tabDesc': 'A description of the second tabbed section.',
            'tables': [
                {
                    'tableTitle':'Table 3',
                    'tableDesc':'A description of table 1.',
                    'tableLayout':[['A','B','C'],['D','E','F']],
                    'tableParams':{'A':param.String('A')}
                },
                {
                    'tableTitle':'Table 4',
                    'tableDesc':'A description of table 1.',
                    'tableLayout':[['A','H','I'],['J','K','L']],
                    'tableParams':{}
                }
            ]
        }
    ]
}
     
s = surveyClass(**surveyDefinition)
s.show().servable()