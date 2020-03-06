import json
import param 
import panel as pn
import itertools as it
pn.extension()

def tableFactory(survey, definition):
    _tbl = type(f"t_{definition['name']}",(surveyTable,),{})
    tbl = _tbl()
    tbl.define(survey, definition)
    
    return tbl

class surveyTab(object):
    
    def __init__(self, survey, title, tables):
        
        self.title = title
        self.survey = survey
        self.tables = [tableFactory(survey, table) for table in tables]
    
    def show(self):
        tabLayout = pn.Column()
        for table in self.tables:
            tabLayout.append(table.show())

        return (f"{self.title}", tabLayout)
    
    def save(self):
        tab = []
        for table in self.tables:
            tab.append(table.save())
        return tab
                
                
class surveyTable(param.Parameterized):
    
    def define(self, survey, definition):
        self.survey = survey
                
        self.tableName = definition['name']
        self.tableLayout = definition['layout']
        self.tableDesc = definition['desc']
        self.specifiedParams = definition['params']
        
        for x in it.chain(*self.tableLayout):
            if x in self.specifiedParams.keys():
                self._add_parameter(x, self.specifiedParams[x])
            else:
                self._add_parameter(x, param.Integer(0))
                
    def show(self):
        tbl = pn.Column(pn.pane.Markdown(f"## {self.tableName}"), pn.pane.Markdown(f'{self.tableDesc}'))
        
        for row in self.tableLayout:
            r = pn.Row()
            for cell in row:
                r.append(self.param[cell])
            tbl.append(r)
        
        return tbl
    
    def save(self):
        return self.param.get_param_values()

    
class surveyClass(param.Parameterized):
    
    save_survey = param.Action(lambda x: x.param.trigger('save_survey'), precedence=0.7)
                
    def __init__(self, tabDefs):
        self.surveyName = "Survey"
        self.surveyDesc = "A short survey description"
        self.tabs=[]
        
        for tabDef in tabDefs:
            self.tabs.append(surveyTab(self, **tabDef))
    
    def show(self):
        s = pn.Column(pn.pane.Markdown(f"# {self.surveyName}"), f"{self.surveyDesc}")
        tabs = pn.Tabs()
        for tab in self.tabs:
            tabs.append(tab.show())
        s.append(tabs)
        return s
    
    @param.depends('save_survey', watch=True)
    def save(self):
        tabs = []
        for tab in self.tabs:
            tabs.append(tab.save())
        
        with open('test.txt', 'w') as f:
            f.write(json.dumps(tabs))
        
        return 0

t1 = {
    'name': 'Table 1',
    'desc': 'Some table description for table 1.',
    'layout': [['A','B','C'],['D','E','F']],
    'params': {'A':param.String('A')}
}
t2 = {
    'name': 'Table 2',
    'desc': 'Some table description for table 2.',
    'layout': [['A','H','I'],['J','K','L']],
    'params': {}
}

tab1 = {
    'title': 'Tab 1',
    'tables': [t1, t2] 
}
                
tab2 = {
    'title': 'Tab 2',
    'tables': [t1, t2] 
}
     
s = surveyClass([tab1,tab2])
y = pn.Column(pn.panel(s.param), s.show())
                
y.servable()