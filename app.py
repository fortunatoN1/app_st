import streamlit as st
import pandas as pd
import plotly.express as px
import time



#PG_INSCRICOES
with st.sidebar:
    st.image('logo_epf.png',width=200)

    st.sidebar.header('Relatórios - EPF')
    seletor = st.sidebar.selectbox('Escolha seu relatório',options=['Inscrições','Avaliações'])
    st.image('pref_w.png', width=200)
if seletor == 'Inscrições':
    time.sleep(0.001)


############## INCLUSÃO DOS DADOS ##############

    #Servidores por avaliação
    @st.cache_data
    def load_servidores ():
        url1 = "https://epfsme.rio.br/public/dash/export_json.php?tabela=eventos_avaliacoes&colunas=EVENTO_ID,SERVIDOR_ID,REGIAO_ID_MATRICULA,DATA_HORA_AVALIACAO&filtro=(ACAO_ID%20IN%20(SELECT%20ACAO_ID%20FROM%20eventos_acoes%20WHERE%20(EVENTO_ID%20%3E%20127)%20AND%20(TIPO_ACAO%20=%20%27INSCRICAO%27)))"
        load_servidores = pd.read_json(url1)
        return load_servidores

    #Total de servidores ids inscritos
    servidores = load_servidores()
    total_servidores_id = servidores['SERVIDOR_ID'].nunique()

    #Buscando o Título das formações por EVENTO_ID
    @st.cache_data
    def load_lista_formacoes():
        url2 = "https://epfsme.rio.br/public/dash/export_json.php?tabela=eventos&colunas=EVENTO_ID,TITULO&filtro=(EVENTO_ID%20in%20(SELECT%20EVENTO_ID%20from%20eventos_acoes%20WHERE%20(EVENTO_ID%3E127)%20AND%20(TIPO_ACAO=%27INSCRICAO%27)))"
        load_lista_formacoes = pd.read_json(url2)
        return load_lista_formacoes

    lista_formacoes = load_lista_formacoes()
    lista_formacoes = lista_formacoes.append([{'EVENTO_ID':9999,'TITULO':'TODAS AS FORMAÇÕES'}])
    #Unindo a lista de servidores com a lista de formações para obter uma lista com o Título das formações
    serv_form = pd.merge(lista_formacoes,servidores,on='EVENTO_ID')

    #Substitunindo as ID de Região para os seus nomes
    serv_form.replace(to_replace = [0,1,2,3,4,5,6,7,8,9,10,11,12], value = ['SEM REGIÃO','1ªCRE','2ªCRE','3ªCRE','4ªCRE','5ªCRE','6ªCRE','7ªCRE','8ªCRE','9ªCRE','10ªCRE','11ªCRE','NÍVEL CENTRAL'], inplace = True)

    #Buscando os servidores com cargos e funcoes

    @st.cache_data
    def load_servidores_total():
        url3 = 'https://epfsme.rio.br/public/dash/export_json.php?tabela=servidores&colunas=SERVIDOR_ID,CARGO_ID_MAT1,FUNCAO_MAT1'
        load_servidores_total = pd.read_json(url3)
        return load_servidores_total

    servidores_total = load_servidores_total()
    #Lista de todos os cargos
    @st.cache_data
    def load_lista_cargos():
        url4 = 'https://epfsme.rio.br/public/dash/export_json.php?tabela=servidores&colunas=DISTINCT%20CARGO_ID_MAT1,SERVIDOR_ID,CARGO_MAT1&filtro=CARGO_ID_MAT1%20IN%20(22,23,24,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,72,77,85,86,87,106,107,108,109,110,111,112,113,114,115,116,117,118)'
        load_lista_cargos = pd.read_json(url4)
        return load_lista_cargos

    lista_cargos = load_lista_cargos()

    ############## FIM DA  INCLUSÃO DOS DADOS ##############

    #Criando tabela de TITULO por Servidores
    tbl = serv_form.groupby(['TITULO']).size().reset_index(name='NUM_SERVIDORES')
    tbl = tbl.append([{'TITULO':'TODAS AS FORMAÇÕES','NUM_SERVIDORES':total_servidores_id}])

    #Passando a DATA_HORA_AVALIACAO apenas para o dia (sem hora)
    serv_form['DATA_HORA_AVALIACAO'] = pd.to_datetime(serv_form['DATA_HORA_AVALIACAO'])
    serv_form['DATA'] = serv_form['DATA_HORA_AVALIACAO'].dt.date

    #Tabela para o gráfico de linha - Inscritos por dia
    tbl_line = serv_form.groupby(['TITULO','DATA']).size().reset_index(name='NUM_SERVIDORES')

    #Tabela para o gráfico de barras - Servidores inscritos por cre
    tbl_bar = serv_form.groupby(['TITULO','REGIAO_ID_MATRICULA']).size().reset_index(name='NUM_SERVIDORES')

    #Juntanto a tabela de servidores para incluir o nome dos cargos e das funções (o json só tinha o id)
    tbl_cargos_funcao = pd.merge(servidores_total,lista_cargos, on = 'SERVIDOR_ID').drop(columns='CARGO_ID_MAT1_x').rename(columns={'CARGO_ID_MAT1_y':'CARGO_ID_MAT1'})

    #Incluindo o titulo das formações
    tbl_cargos_funcao_form = pd.merge(tbl_cargos_funcao,serv_form, on = 'SERVIDOR_ID').replace(to_replace = ["",None], value = ["S/ FUNÇÃO GRAT.","S/ FUNÇÃO GRAT."])

    #Agrupando Cargo e TITULO por total de servidores
    cargo_form_grupo = tbl_cargos_funcao_form.groupby(['TITULO','CARGO_MAT1']).size().reset_index(name='NUM_SERVIDORES')

    #Agrupando Cargo e FUNCAO por total de servidores
    funcao_form_grupo = tbl_cargos_funcao_form.groupby(['TITULO','FUNCAO_MAT1']).size().reset_index(name='NUM_SERVIDORES')


    ############### STREAMLIT ######################
    st.markdown("""
    <style>
    .e1fb0mya1.css-fblp2m.ex0cdmw0
    {
        visibility: hidden;
    }
    .css-cio0dv.egzxvld1
    {
        visibility: hidden;
    }
 
    </style>
    """,unsafe_allow_html = True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.title('Relatório de Inscrições')
    with c2:
        st.empty()
    with c3:
        st.image('LogoPrincipal.png', width=150, use_column_width=False)




    c1,c2,c3 = st.columns(3)

    with c1:
        f_formacao = st.selectbox(label='Selecione a formação',options=lista_formacoes['TITULO'].unique(),)
    with c2:
        st.empty()

    with c3:
            try:
                valor_metrica = tbl.query('TITULO == @f_formacao')['NUM_SERVIDORES'].item()
            except ValueError:
                valor_metrica = 0
            st.metric(label='Servidores inscritos',value=valor_metrica,delta='CPF',delta_color='off')
    st.write('---')
    col1,col2 = st.columns(2)

    with col1:
        st.write('Distribuição por cargos')
        t1, t2 = st.tabs(['Gráfico', 'Tabela'])
        cargo_fig = cargo_form_grupo.query('TITULO == @f_formacao')[['CARGO_MAT1', 'NUM_SERVIDORES']]
        if f_formacao !='TODAS AS FORMAÇÕES':
            t1.plotly_chart(px.pie(cargo_fig,values='NUM_SERVIDORES',names = 'CARGO_MAT1'))
            t2.dataframe(cargo_fig)
        else:
            cargo_form_grupo_total = tbl_cargos_funcao_form.groupby(['CARGO_MAT1']).size().reset_index(name='NUM_SERVIDORES')
            t1.plotly_chart(px.pie(cargo_form_grupo_total,values='NUM_SERVIDORES',names = 'CARGO_MAT1'))
            t2.dataframe(cargo_form_grupo_total)


    with col2:
        st.write('Distribuição por função')
        t1, t2 = st.tabs(['Gráfico', 'Tabela'])
        funcao_fig = funcao_form_grupo.query('TITULO == @f_formacao')[['FUNCAO_MAT1', 'NUM_SERVIDORES']]
        if f_formacao !='TODAS AS FORMAÇÕES':
            t1.plotly_chart(px.pie(funcao_fig,values='NUM_SERVIDORES',names = 'FUNCAO_MAT1'))
            t2.dataframe(funcao_fig)
        else:
            funcao_form_grupo_total = tbl_cargos_funcao_form.groupby(['FUNCAO_MAT1']).size().reset_index(name='NUM_SERVIDORES')
            t1.plotly_chart(px.pie(funcao_form_grupo_total, values='NUM_SERVIDORES', names='FUNCAO_MAT1'))
            t2.dataframe(funcao_form_grupo_total)

    st.write('---')
    c1,c2 = st.columns(2)

    with c1:
        st.write('  Quantidade de inscritos por dia:')
        t1,t2 = st.tabs(['Gráfico','Tabela'])

        if f_formacao !='TODAS AS FORMAÇÕES':
            line = tbl_line.loc[tbl_line['TITULO']==f_formacao].drop(columns=['TITULO'])
            t1.line_chart(line,x='DATA',y='NUM_SERVIDORES')
            t2.dataframe(line)
        else:
            tbl_line_total = serv_form.groupby(['DATA']).size().reset_index(name='NUM_SERVIDORES')
            t1.line_chart(tbl_line_total, x='DATA', y='NUM_SERVIDORES')
            t2.dataframe(tbl_line_total)

    with c2:
        st.write('  Quantidade de inscritos por Região:')
        tab1,tab2 = st.tabs(['Gráfico','Tabela'])
        if f_formacao != 'TODAS AS FORMAÇÕES':
            tab1.bar_chart(tbl_bar.query('TITULO == @f_formacao and REGIAO_ID_MATRICULA!=""')[['NUM_SERVIDORES','REGIAO_ID_MATRICULA']],x='REGIAO_ID_MATRICULA',y = 'NUM_SERVIDORES')
            tab2.dataframe(tbl_bar.query('TITULO == @f_formacao and REGIAO_ID_MATRICULA!=""')[['NUM_SERVIDORES','REGIAO_ID_MATRICULA']])
        else:
            tbl_bar_total = serv_form.groupby(['REGIAO_ID_MATRICULA']).size().reset_index(name='NUM_SERVIDORES')
            tab1.bar_chart(tbl_bar_total, x='REGIAO_ID_MATRICULA', y='NUM_SERVIDORES')
            tab2.dataframe(tbl_bar_total)
else:
    st.title('Calma Carai')
