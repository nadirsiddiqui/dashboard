import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import dash
from jupyter_dash import JupyterDash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

gss = pd.read_csv("https://github.com/jkropko/DS-6001/raw/master/localdata/gss2018.csv",
                 encoding='cp1252', na_values=['IAP','IAP,DK,NA,uncodeable', 'NOT SURE',
                                               'DK', 'IAP, DK, NA, uncodeable', '.a', "CAN'T CHOOSE"])

mycols = ['id', 'wtss', 'sex', 'educ', 'region', 'age', 'coninc',
          'prestg10', 'mapres10', 'papres10', 'sei10', 'satjob',
          'fechld', 'fefam', 'fepol', 'fepresch', 'meovrwrk'] 
gss_clean = gss[mycols]
gss_clean = gss_clean.rename({'wtss':'weight', 
                              'educ':'education', 
                              'coninc':'income', 
                              'prestg10':'job_prestige',
                              'mapres10':'mother_job_prestige', 
                              'papres10':'father_job_prestige', 
                              'sei10':'socioeconomic_index', 
                              'fechld':'relationship', 
                              'fefam':'male_breadwinner', 
                              'fehire':'hire_women', 
                              'fejobaff':'preference_hire_women', 
                              'fepol':'men_bettersuited', 
                              'fepresch':'child_suffer',
                              'meovrwrk':'men_overwork'},axis=1)
gss_clean.age = gss_clean.age.replace({'89 or older':'89'})
gss_clean.age = gss_clean.age.astype('float')

string1 = "According to the Federal Reserve Bank of St. Louis, most of the gap in wages between genders is attributed to weekly vs. hourly wages,\neducation, \
experience, occupation, and union status. The Bank claims that since women typically work fewer hours than men and have lower\neducation \
and experience than men, the wage gap may reveal 'underlying expectations and social norms that drive our career and workforce \ndecisions.'"

string2 = "Another article from NPR discusses how in typical recessions, men's unemployment numbers rise significantly while many women enter the \nworkforce \
or increase their hours. NPR cites this phenomenon to how consumer-focused corporations disproportionately hire men while women \ntend to \
work in areas such as 'education, health care, and in-person services.'"

string3 = "To help understand the wage gap, we can examine the General Social Survey (GSS), a survey that monitors 'trends in opinions, attitudes, and \nbehaviors' \
in adults in the United States. It contains variables such as mean income, occupational prestige, education, and socioeconomic index; \nall \
are able to be grouped by sex which will provide insight to the matter at hand."

links = "Sources: \nhttps://www.stlouisfed.org/publications/regional-economist/april-2001/how-much-of-the-gender-wage-gap-is-due-to-discrimination\n\
https://www.npr.org/sections/money/2020/08/18/903221371/how-the-pandemic-is-making-the-gender-pay-gap-worse"


table = gss_clean.groupby('sex').agg({'income':'mean',
                               'job_prestige':'mean',
                               'socioeconomic_index':'mean',
                               'education':'mean'}).reset_index()
table = table.rename({'job_prestige':'Occupational Prestige',
                                        'socioeconomic_index':'Socioeconomic Index',
                                        'education':'Years of Education',
                                        'income':'Mean Income',
                                        'sex':'Sex'}, axis=1)
table2 = ff.create_table(round(table,2))


gss_bar = pd.crosstab(gss_clean.male_breadwinner, gss_clean.sex).reset_index()
gss_bar = pd.melt(gss_bar, id_vars = 'male_breadwinner', value_vars = ['female', 'male'])
gss_bar['male_breadwinner'] = gss_bar['male_breadwinner'].astype('category')
gss_bar['male_breadwinner'] = gss_bar['male_breadwinner'].cat.reorder_categories(['strongly disagree','disagree',
                                                                                  'agree', 'strongly agree'])
gss_bar = gss_bar.sort_values('male_breadwinner')
fig1 = px.bar(gss_bar, x='male_breadwinner', y='value', color='sex',
            barmode = 'group',
            labels={'value':'Count', 'male_breadwinner':'Level of Agreement'})


fig2 = px.scatter(gss_clean, x='job_prestige', y='income', 
                 color='sex',
                 trendline='ols',
                 height=600, width=600,
                 labels={'job_prestige':'Occupational Prestige', 
                        'income':'Mean Income'},
                 hover_data=['education', 'socioeconomic_index'])
fig2 = fig2.update(layout=dict(title=dict(x=0.5)))


fig3 = px.box(gss_clean, x='income', y = 'sex', color = 'sex',
                   labels={'income':'Mean Income',
                           'sex':'Sex'})
fig3 = fig3.update_layout(showlegend=False)



fig4 = px.box(gss_clean, x='job_prestige', y = 'sex', color = 'sex',
                   labels={'job_prestige':'Occupational Prestige',
                           'sex':'Sex'})
fig4 = fig4.update_layout(showlegend=False)


gss_new = gss_clean[['income', 'sex', 'job_prestige']]
gss_new['job_prestige_cat'] = pd.cut(gss_new.job_prestige, bins=6)
gss_new = gss_new.sort_values('job_prestige_cat').dropna()

fig5 = px.box(gss_new, x='income', y = 'sex', color = 'sex',
             color_discrete_map = {'male':'blue', 'female':'orange'},
             facet_col='job_prestige_cat', facet_col_wrap=2,
                   labels={'job_prestige':'Occupational Prestige',
                           'sex':'Sex'})
fig5 = fig5.update_layout(showlegend=False)


app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    
        html.H2("Exploring the Wage Gap using the 2019 General Social Survey"),   
        dcc.Markdown(string1),
        dcc.Markdown(string2),
        dcc.Markdown(string3),
        dcc.Markdown(links),
    
        html.H4("Mean Income by Sex"),   
        dcc.Graph(figure = table2),
    
        html.H4("Opinion on: 'It is much better for everyone involved if the man is the achiever outside the home and the woman takes care of the home and family.':"), 
        dcc.Graph(figure = fig1),
    
        html.H4("Mean Income against Job Prestige"), 
        dcc.Graph(figure = fig2),
    
        html.Div([
            
            html.H4("Distribution of Mean Income by Sex"),            
            dcc.Graph(figure=fig3)
            
        ], style = {'width':'48%', 'float':'left'}),
        
        html.Div([
            
            html.H4("Distribution of Job Prestige by Sex"),
            dcc.Graph(figure=fig4)
            
        ], style = {'width':'48%', 'float':'right'}),
        
        html.H4("Mean Income by Sex and Job Prestige Category"),
        dcc.Graph(figure = fig5),
    
    ])

    

if __name__ == '__main__':
    app.run_server(debug=True)
