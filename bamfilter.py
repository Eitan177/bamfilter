import streamlit as st
import re
import pandas as pd
import numpy as np



def convert_df(df,topofsam):
    topofsam='\n'.join(topofsam)
    df.rename(columns={'0':topofsam},inplace=True)
    return df.to_csv(index=False,header=False,sep='\t').encode('utf-8')

with st.form(key='file upload'):
    # Add form elements
    uploaded_file = st.file_uploader("Upload a sam file")
    selected_option = st.multiselect('Select options for filtering', ['softclip', 'deletion', 'insertion'],['softclip'])
    query = st.text_input("Filter dataframe")
    posorneg = st.radio('filter type',['In','Not in'])
    # Add a form submit button
    submitted = st.form_submit_button('Submit')
mm=[]
reads=[]
pattern = '^@'
if submitted:
    if uploaded_file is not None:
        file_contents = uploaded_file.getvalue().decode("utf-8")
        for line in file_contents.split('\n'):
            if re.findall(pattern, line):
                mm.append(line)
            elif re.findall('[0-9]',line):
                reads.append(line)

        #st.write(mm)
        df=pd.DataFrame({'reads':reads})
        df_split = df['reads'].str.split('\t', expand=True)
        # Read the split strings into a new DataFrame
        new_df = pd.DataFrame(df_split)
    
        new_df.columns=[str(a) for a in np.arange(0,new_df.shape[1])]
        reads_use=pd.DataFrame()
        if 'softclip' in selected_option:
            reads_use=pd.concat([reads_use,new_df.loc[new_df['5'].str.contains('S')]])
           
        if 'deletion' in selected_option:
            reads_use=pd.concat([reads_use,new_df.loc[new_df['5'].str.contains('D')]])  
        if 'insertion' in selected_option:
            reads_use=pd.concat([reads_use,new_df.loc[new_df['5'].str.contains('I')]]) 
        if query:
            if posorneg =='In':
                mask = reads_use.map(lambda x: query in str(x).lower()).any(axis=1)
                reads_use = reads_use[mask] 
                st.write(mask)
            else:
                mask = reads_use.map(lambda x: query in str(x).lower()).any(axis=1) 
                st.write(mask)
                reads_use = pd.merge(reads_use,reads_use[mask], how='left') 
        st.data_editor(reads_use)
        st.write(reads_use.shape)
        reads_use=convert_df(reads_use,mm)   
        
        st.download_button('Download filtered sam',reads_use,'filtered.sam','text')
