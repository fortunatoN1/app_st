import re
import numpy as np
import plotly.graph_objects as go
import streamlit as st
import pandas as pd
import plotly.express as px
import time

st.set_page_config(layout="wide", initial_sidebar_state='expanded')


with st.sidebar:

    st.image('LogoPrincipal.png', width=200, use_column_width=False)
    st.sidebar.header('Relatórios - EPF')
    seletor = st.sidebar.selectbox('Escolha seu relatório', options=['Inscrições', 'Avaliações'])
    st.image('pref_w.png', width=200)

###################################  PÁGINA DE INSCRIÇÕES ###################################
if seletor == 'Inscrições':
    time.sleep(0.001)
    # EDITANDO CSS #

    st.markdown("""
    <style>

    .css-10pw50.egzxvld1
    {
        visibility: hidden;
    }
    .viewerBadge_link__1S137
    {
        visibility: hidden;
    }
    .css-1wbqy5l.e10z71041
    {
        visibility: hidden;
    }
    .css-cio0dv.egzxvld1
    {
        visibility: hidden;
    }
    </style>
    """, unsafe_allow_html=True)

    ############## INCLUSÃO DOS DADOS ##############

    # Servidores por avaliação

    def load_servidores():
        url1 = "https://epfsme.rio.br/public/dash/export_json.php?tabela=eventos_avaliacoes&colunas=EVENTO_ID,SERVIDOR_ID,REGIAO_ID_MATRICULA,DATA_HORA_AVALIACAO&filtro=(ACAO_ID%20IN%20(SELECT%20ACAO_ID%20FROM%20eventos_acoes%20WHERE%20(EVENTO_ID%20%3E%20127)%20AND%20(TIPO_ACAO%20=%20%27INSCRICAO%27)))"
        load_servidores = pd.read_json(url1)
        return load_servidores


    # Total de servidores ids inscritos
    servidores = load_servidores()
    total_servidores_id = servidores['SERVIDOR_ID'].nunique()


    # Buscando o Título das formações por EVENTO_ID

    def load_lista_formacoes():
        url2 = "https://epfsme.rio.br/public/dash/export_json.php?tabela=eventos&colunas=EVENTO_ID,TITULO&filtro=(EVENTO_ID%20in%20(SELECT%20EVENTO_ID%20from%20eventos_acoes%20WHERE%20(EVENTO_ID%3E127)%20AND%20(TIPO_ACAO=%27INSCRICAO%27)))"
        load_lista_formacoes = pd.read_json(url2)
        return load_lista_formacoes


    lista_formacoes = load_lista_formacoes()
    lista_formacoes = lista_formacoes.append([{'EVENTO_ID': 9999, 'TITULO': 'TODAS AS FORMAÇÕES'}])
    # Unindo a lista de servidores com a lista de formações para obter uma lista com o Título das formações
    serv_form = pd.merge(lista_formacoes, servidores, on='EVENTO_ID')

    # Substitunindo as ID de Região para os seus nomes
    serv_form.replace(to_replace=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                      value=['SEM REGIÃO', '1ªCRE', '2ªCRE', '3ªCRE', '4ªCRE', '5ªCRE', '6ªCRE', '7ªCRE', '8ªCRE',
                             '9ªCRE', '10ªCRE', '11ªCRE', 'NÍVEL CENTRAL'], inplace=True)


    # Buscando os servidores com cargos e funcoes

    @st.cache_data
    def load_servidores_total():
        url3 = 'https://epfsme.rio.br/public/dash/export_json.php?tabela=servidores&colunas=SERVIDOR_ID,CARGO_ID_MAT1,FUNCAO_MAT1'
        load_servidores_total = pd.read_json(url3)
        return load_servidores_total


    servidores_total = load_servidores_total()


    # Lista de todos os cargos
    @st.cache_data
    def load_lista_cargos():
        url4 = 'https://epfsme.rio.br/public/dash/export_json.php?tabela=servidores&colunas=DISTINCT%20CARGO_ID_MAT1,SERVIDOR_ID,CARGO_MAT1&filtro=CARGO_ID_MAT1%20IN%20(22,23,24,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,72,77,85,86,87,106,107,108,109,110,111,112,113,114,115,116,117,118)'
        load_lista_cargos = pd.read_json(url4)
        return load_lista_cargos


    lista_cargos = load_lista_cargos()

    ############## FIM DA  INCLUSÃO DOS DADOS ##############

    # Criando tabela de TITULO por Servidores
    tbl = serv_form.groupby(['TITULO']).size().reset_index(name='NUM_SERVIDORES')
    tbl = tbl.append([{'TITULO': 'TODAS AS FORMAÇÕES', 'NUM_SERVIDORES': total_servidores_id}])

    # Passando a DATA_HORA_AVALIACAO apenas para o dia (sem hora)
    serv_form['DATA_HORA_AVALIACAO'] = pd.to_datetime(serv_form['DATA_HORA_AVALIACAO'])
    serv_form['DATA'] = serv_form['DATA_HORA_AVALIACAO'].dt.date

    # Tabela para o gráfico de linha - Inscritos por dia
    tbl_line = serv_form.groupby(['TITULO', 'DATA']).size().reset_index(name='NUM_SERVIDORES')

    # Tabela para o gráfico de barras - Servidores inscritos por cre
    tbl_bar = serv_form.groupby(['TITULO', 'REGIAO_ID_MATRICULA']).size().reset_index(name='NUM_SERVIDORES')

    # Juntanto a tabela de servidores para incluir o nome dos cargos e das funções (o json só tinha o id)
    tbl_cargos_funcao = pd.merge(servidores_total, lista_cargos, on='SERVIDOR_ID').drop(
        columns='CARGO_ID_MAT1_x').rename(columns={'CARGO_ID_MAT1_y': 'CARGO_ID_MAT1'})

    # Incluindo o titulo das formações
    tbl_cargos_funcao_form = pd.merge(tbl_cargos_funcao, serv_form, on='SERVIDOR_ID').replace(to_replace=["", None],
                                                                                              value=["S/ FUNÇÃO GRAT.",
                                                                                                     "S/ FUNÇÃO GRAT."])

    # Agrupando Cargo e TITULO por total de servidores
    cargo_form_grupo = tbl_cargos_funcao_form.groupby(['TITULO', 'CARGO_MAT1']).size().reset_index(
        name='NUM_SERVIDORES')

    # Agrupando Cargo e FUNCAO por total de servidores
    funcao_form_grupo = tbl_cargos_funcao_form.groupby(['TITULO', 'FUNCAO_MAT1']).size().reset_index(
        name='NUM_SERVIDORES')

    ############### STREAMLIT ######################

    c1, c2, c3 = st.columns(3)
    with c1:
        st.title('Relatório de Inscrições')
    with c2:
        st.empty()
    with c3:
        st.empty()

    c1, c2, c3 = st.columns(3)

    with c1:
        f_formacao = st.selectbox(label='Selecione a formação', options=lista_formacoes['TITULO'].unique(), )
    with c2:
        st.empty()

    with c3:
        try:
            valor_metrica = tbl.query('TITULO == @f_formacao')['NUM_SERVIDORES'].item()
        except ValueError:
            valor_metrica = 0
        st.plotly_chart(go.Figure(go.Indicator(
            mode='number',
            value=valor_metrica,
            number={"font_size": 35},
            title={"text": "Servidores Inscritos (total de CPF)", "font_size": 16}

        )).update_layout(paper_bgcolor="rgba(100,100,100,0.1)",
                         height=80,
                         margin_t=400,
                         margin_b=250,
                         ), use_container_width=True)
    st.write('---')
    col1, col2 = st.columns(2)

    with col1:
        st.write('Distribuição por cargos')
        t1, t2 = st.tabs(['Gráfico', 'Tabela'])
        cargo_fig = cargo_form_grupo.query('TITULO == @f_formacao')[['CARGO_MAT1', 'NUM_SERVIDORES']]
        if f_formacao != 'TODAS AS FORMAÇÕES':
            t1.plotly_chart(px.pie(cargo_fig, values='NUM_SERVIDORES', names='CARGO_MAT1', hole=.3).update_traces(
                textposition='inside'))
            t2.dataframe(cargo_fig)
        else:
            cargo_form_grupo_total = tbl_cargos_funcao_form.groupby(['CARGO_MAT1']).size().reset_index(
                name='NUM_SERVIDORES')
            t1.plotly_chart(
                px.pie(cargo_form_grupo_total, values='NUM_SERVIDORES', names='CARGO_MAT1', hole=.3).update_traces(
                    textposition='inside'))
            t2.dataframe(cargo_form_grupo_total)

    with col2:
        st.write('Distribuição por função')
        t1, t2 = st.tabs(['Gráfico', 'Tabela'])
        funcao_fig = funcao_form_grupo.query('TITULO == @f_formacao')[['FUNCAO_MAT1', 'NUM_SERVIDORES']]
        if f_formacao != 'TODAS AS FORMAÇÕES':
            t1.plotly_chart(px.pie(funcao_fig, values='NUM_SERVIDORES', names='FUNCAO_MAT1'))
            t2.dataframe(funcao_fig)
        else:
            funcao_form_grupo_total = tbl_cargos_funcao_form.groupby(['FUNCAO_MAT1']).size().reset_index(
                name='NUM_SERVIDORES')
            t1.plotly_chart(px.pie(funcao_form_grupo_total, values='NUM_SERVIDORES', names='FUNCAO_MAT1'))
            t2.dataframe(funcao_form_grupo_total)

    st.write('---')
    c1, c2 = st.columns(2)

    with c1:
        st.write('  Quantidade de inscritos por dia:')
        t1, t2 = st.tabs(['Gráfico', 'Tabela'])

        if f_formacao != 'TODAS AS FORMAÇÕES':
            line = tbl_line.loc[tbl_line['TITULO'] == f_formacao].drop(columns=['TITULO'])
            t1.line_chart(line, x='DATA', y='NUM_SERVIDORES')
            t2.dataframe(line)
        else:
            tbl_line_total = serv_form.groupby(['DATA']).size().reset_index(name='NUM_SERVIDORES')
            t1.line_chart(tbl_line_total, x='DATA', y='NUM_SERVIDORES')
            t2.dataframe(tbl_line_total)

    with c2:
        st.write('  Quantidade de inscritos por Região:')
        tab1, tab2 = st.tabs(['Gráfico', 'Tabela'])
        if f_formacao != 'TODAS AS FORMAÇÕES':
            tab1.bar_chart(tbl_bar.query('TITULO == @f_formacao and REGIAO_ID_MATRICULA!=""')[
                               ['NUM_SERVIDORES', 'REGIAO_ID_MATRICULA']], x='REGIAO_ID_MATRICULA', y='NUM_SERVIDORES')
            tab2.dataframe(tbl_bar.query('TITULO == @f_formacao and REGIAO_ID_MATRICULA!=""')[
                               ['NUM_SERVIDORES', 'REGIAO_ID_MATRICULA']])
        else:
            tbl_bar_total = serv_form.groupby(['REGIAO_ID_MATRICULA']).size().reset_index(name='NUM_SERVIDORES')
            tab1.bar_chart(tbl_bar_total, x='REGIAO_ID_MATRICULA', y='NUM_SERVIDORES')
            tab2.dataframe(tbl_bar_total)

################################################  PAGINA DE AVALIAÇÕES   ################################################
else:

    # EDITANDO CSS #

    st.markdown("""
    <style>

    .css-10pw50.egzxvld1
    {
        visibility: hidden;
    }
    .viewerBadge_link__1S137
    {
        visibility: hidden;
    }
    .css-1wbqy5l.e10z71041
    {
        visibility: hidden;
    }
    .css-cio0dv.egzxvld1
    {
        visibility: hidden;
    }
    </style>
    """, unsafe_allow_html=True)


    ## QUERY DE DADOS ##

    # Lista de servidores que avaliaram alguma ação

    def load_serv_av():
        url = "https://epfsme.rio.br/public/dash/export_json.php?tabela=eventos_avaliacoes&colunas=EVENTO_ID,SERVIDOR_ID,REGIAO_ID_MATRICULA,DATA_HORA_AVALIACAO,json_extract(RESPOSTAS,%27$.q00p011r01%27),json_extract(RESPOSTAS,'$.q01p070r01'),json_extract(RESPOSTAS,'$.q01p080r01'),json_extract(RESPOSTAS,'$.q01p090r01')&filtro=(ACAO_ID%20IN%20(SELECT%20ACAO_ID%20FROM%20eventos_acoes%20WHERE%20(EVENTO_ID%20%3E%20127)%20AND%20(TIPO_ACAO%20=%20%27AVALIACAO%27)))"
        load_serv_av = pd.read_json(url)
        return load_serv_av


    serv_av = load_serv_av()


    # Lista de eventos de avaliação

    def load_eventos_av():
        url = "https://epfsme.rio.br/public/dash/export_json.php?tabela=eventos&colunas=EVENTO_ID,TITULO&filtro=(EVENTO_ID%20in%20(SELECT%20EVENTO_ID%20from%20eventos_acoes%20WHERE%20(EVENTO_ID%3E127)%20AND%20(TIPO_ACAO=%27AVALIACAO%27)))"
        load_eventos_av = pd.read_json(url)
        return load_eventos_av


    eventos_av = load_eventos_av()


    # Lista de cargos de respecttivos servidores IDs - REVER: Já tem esse dado na tabela servidores do BD (10/04/23)
    @st.cache_data
    def load_lista_cargos():
        url = 'https://epfsme.rio.br/public/dash/export_json.php?tabela=servidores&colunas=DISTINCT%20SERVIDOR_ID,CARGO_MAT1'
        load_lista_cargos = pd.read_json(url)
        return load_lista_cargos


    lista_cargos = load_lista_cargos()


    # Lista de servidores inscritos nas ações

    def load_inscritos():
        url = "https://epfsme.rio.br/public/dash/export_json.php?tabela=eventos_avaliacoes&colunas=EVENTO_ID,SERVIDOR_ID,REGIAO_ID_MATRICULA,json_extract(RESPOSTAS,%27$.q01p010r02%27)&filtro=(ACAO_ID%20IN%20(SELECT%20ACAO_ID%20FROM%20eventos_acoes%20WHERE%20(EVENTO_ID%20%3E%20129)%20AND%20(TIPO_ACAO%20=%20%27INSCRICAO%27)))"
        load_inscritos = pd.read_json(url)
        return load_inscritos


    inscritos = load_inscritos()

    # Resolvendo o retorno do JSON na forma string_json
    serv_av['json_extract(RESPOSTAS,\'$.q01p070r01\')'] = serv_av['json_extract(RESPOSTAS,\'$.q01p070r01\')'].fillna(
        0).apply(lambda x: int(re.search(r'\d+', str(x)).group()))
    serv_av['json_extract(RESPOSTAS,\'$.q01p080r01\')'] = serv_av['json_extract(RESPOSTAS,\'$.q01p080r01\')'].fillna(
        0).apply(lambda x: int(re.search(r'\d+', str(x)).group()))
    serv_av['json_extract(RESPOSTAS,\'$.q01p090r01\')'] = serv_av['json_extract(RESPOSTAS,\'$.q01p090r01\')'].fillna(
        0).apply(lambda x: int(re.search(r'\d+', str(x)).group()))

    serv_av['json_extract(RESPOSTAS,\'$.q01p070r01\')'] = serv_av['json_extract(RESPOSTAS,\'$.q01p070r01\')'].fillna(
        0).apply(lambda x: int(str(x).strip('"')))
    serv_av['json_extract(RESPOSTAS,\'$.q01p080r01\')'] = serv_av['json_extract(RESPOSTAS,\'$.q01p080r01\')'].fillna(
        0).apply(lambda x: int(str(x).strip('"')))
    serv_av['json_extract(RESPOSTAS,\'$.q01p090r01\')'] = serv_av['json_extract(RESPOSTAS,\'$.q01p090r01\')'].fillna(
        0).apply(lambda x: int(str(x).strip('"')))

    # Juntando as tabelas de servidores com os eventos para buscar o titulo + adicionando a coluna turma
    serv_eventos_av = pd.merge(serv_av, eventos_av, on="EVENTO_ID").rename(
        columns={"json_extract(RESPOSTAS,'$.q00p011r01')": 'Turma',
                 "json_extract(RESPOSTAS,'$.q01p070r01')": 'Nota da Formação',
                 "json_extract(RESPOSTAS,'$.q01p080r01')": 'Nota NPS',
                 "json_extract(RESPOSTAS,'$.q01p090r01')": 'Nota Aplicação'})
    # Juntando o resultado da tabela anterior com os cargos
    serv_eventos_av_cargo = pd.merge(serv_eventos_av, lista_cargos, on='SERVIDOR_ID')


    # Calculando o índice NPS para cada resposta
    def classifica_nps(nota):
        if nota < 7:
            return 'Detrator'
        elif nota <= 8:
            return 'Neutro'
        else:
            return 'Promotor'


    serv_eventos_av_cargo['Status_NPS'] = serv_eventos_av_cargo['Nota NPS'].apply(classifica_nps)
    # Trocando NONE,sim e Não das turmas para as CRES
    serv_eventos_av_cargo.loc[serv_eventos_av_cargo['Turma'].isin([None, 'Sim', 'Não']), 'Turma'] = \
    serv_eventos_av_cargo['REGIAO_ID_MATRICULA'].astype(str) + 'ªCRE'

    # Simplificando a tabela serv_eventos_av_cargos em av
    av = serv_eventos_av_cargo
    # Adicionando a opção "TODAS"
    av = av.append(
        {'EVENTO_ID': 999, 'SERVIDOR_ID': "", 'REGIAO_ID_MATRICULA': 'TODAS AS REGIÕES', 'Turma': "TODAS AS TURMAS",
         'Nota da Formação': '', 'Nota NPS': '', 'Nota Aplicação': '', 'TITULO': 'TODAS AS FORMAÇÕES',
         'CARGO_MAT1': 'TODOS OS CARGOS', 'Status_NPS': ''}, ignore_index=True)
    av['Turma'] = av['Turma'].str.replace('"', '')

    # Trabalhando com a tabela de inscritos
    inscritos_titulo = pd.merge(inscritos, eventos_av, on="EVENTO_ID").rename(
        columns={"json_extract(RESPOSTAS,'$.q01p010r02')": 'Turma'})
    inscritos_titulo['Turma'] = inscritos_titulo['Turma'].str.replace('"', '')
    inscritos_titulo.loc[inscritos_titulo['Turma'].isin([None]), 'Turma'] = inscritos_titulo['REGIAO_ID_MATRICULA'].astype(str) + 'ªCRE'
    inscritos_titulo_cargo = pd.merge(inscritos_titulo, lista_cargos, on='SERVIDOR_ID')

    # Adicionando as avaliações da JORNADA 2023 como inscrição já que não houve a inscrição dessa formação
    av_inscrever = av.query("TITULO =='JORNADA DE PLANEJAMENTO, FORMAÇÃO PEDAGÓGICA E CENTRO DE ESTUDOS 2023'")[['EVENTO_ID', 'SERVIDOR_ID', 'REGIAO_ID_MATRICULA', 'Turma', 'TITULO', 'CARGO_MAT1']]
    av_inscrever_balaio = av.query("TITULO =='BALAIO DE LIVROS'")[['EVENTO_ID', 'SERVIDOR_ID', 'REGIAO_ID_MATRICULA', 'Turma', 'TITULO', 'CARGO_MAT1']]
    inscritos_final = pd.concat([av_inscrever, av_inscrever_balaio,inscritos_titulo_cargo])




    # Avaliações por CRE



    # Inscrições por CRE



    #   STREAMLIT   #

    st.title('Avaliações')
    # Filtro Formação

    c1, c2,c3 = st.columns(3)
    with c1:
        sel_formacao = st.selectbox(label='Selecione a formação:', options=av['TITULO'].unique(),
                                    index=pd.DataFrame(av['TITULO'].unique()).index[-1])
        sel_cargos = st.empty()
        sel_turma = st.empty()

        cargo_list = np.array(av.loc[av['TITULO'] == sel_formacao,'CARGO_MAT1'].unique())
        todos_cargos_list = np.array(av['CARGO_MAT1'].unique())

        turma_list = av.loc[av['TITULO'] == sel_formacao,'Turma'].unique()
        turma_list = np.append(turma_list,'TODAS AS TURMAS')



        # Filtro cargo
        sel_cargos = st.selectbox(label='Selecione o cargo:', options=np.roll(todos_cargos_list,1))

        # Filtro turma
        if sel_formacao == 'TODAS AS FORMAÇÕES':
            st.empty()
        else:  # sel_formacao != 'TODAS AS FORMAÇÕES'and sel_cargos == 'Todos'
            sel_turma = st.selectbox(label='Selecione a turma:', options=np.roll(turma_list,1))
        # elif sel_formacao != 'TODAS AS FORMAÇÕES' and sel_cargos != 'Todos':
        # sel_turma = st.selectbox(label='Selecione a turma:',options=np.append(turma_list,'Todas'),index=pd.DataFrame(np.append(turma_list,'Todas')).index[-1])

        # Calculo NPS ; Total de inscritos ; Total de avaliacoes
        detratores = 0
        neutros = 0
        promotores = 0
        total = 0

        # Medias
        nota_formacao = 0
        nota_aplicacao = 0

        if sel_formacao == 'TODAS AS FORMAÇÕES' and sel_cargos == 'TODOS OS CARGOS':
            detratores = len(av.query("Status_NPS == 'Detrator'"))
            neutros = len(av.query("Status_NPS == 'Neutro'"))
            promotores = len(av.query("Status_NPS == 'Promotor'"))

            inscritos_total = len(inscritos_final.query("SERVIDOR_ID != ''"))
            total = len(av.query("SERVIDOR_ID != ''"))

            nota_formacao = int(float((format(av.query("TITULO !='JORNADA DE PLANEJAMENTO, FORMAÇÃO PEDAGÓGICA E CENTRO DE ESTUDOS 2023' and SERVIDOR_ID != ''")['Nota da Formação'].mean(), '.1f'))) * 10)
            nota_aplicacao = int(float((format(av.query("TITULO !='JORNADA DE PLANEJAMENTO, FORMAÇÃO PEDAGÓGICA E CENTRO DE ESTUDOS 2023' and SERVIDOR_ID != ''")['Nota Aplicação'].mean(), '.1f'))) * 10)

            cre_tab = av.query("SERVIDOR_ID != ''")[['REGIAO_ID_MATRICULA', 'SERVIDOR_ID']]
            inscritos_final_cre = inscritos_final.query("SERVIDOR_ID != ''")[['REGIAO_ID_MATRICULA', 'SERVIDOR_ID']]

        elif sel_formacao == 'TODAS AS FORMAÇÕES' and sel_cargos != 'TODOS OS CARGOS':
            detratores = len(av.query("CARGO_MAT1 == @sel_cargos and Status_NPS == 'Detrator'"))
            neutros = len(av.query("CARGO_MAT1 == @sel_cargos and Status_NPS == 'Neutro'"))
            promotores = len(av.query("CARGO_MAT1 == @sel_cargos and Status_NPS == 'Promotor'"))

            inscritos_total = len(inscritos_final.query('CARGO_MAT1 == @sel_cargos'))
            total = len(av.query("CARGO_MAT1 == @sel_cargos and Status_NPS != ''"))

            nota_formacao = int(float((format(av.query("TITULO !='JORNADA DE PLANEJAMENTO, FORMAÇÃO PEDAGÓGICA E CENTRO DE ESTUDOS 2023' and CARGO_MAT1 == @sel_cargos")['Nota da Formação'].mean(), '.0f'))) * 10)
            nota_aplicacao = int(float((format(av.query("TITULO !='JORNADA DE PLANEJAMENTO, FORMAÇÃO PEDAGÓGICA E CENTRO DE ESTUDOS 2023' and CARGO_MAT1 == @sel_cargos")['Nota Aplicação'].mean(), '.0f'))) * 10)

            cre_tab = av.query("CARGO_MAT1 == @sel_cargos and Status_NPS != ''")[['REGIAO_ID_MATRICULA', 'SERVIDOR_ID']]
            inscritos_final_cre = inscritos_final.query('CARGO_MAT1 == @sel_cargos')[['REGIAO_ID_MATRICULA', 'SERVIDOR_ID']]

        elif sel_formacao != 'TODAS AS FORMAÇÕES' and sel_cargos != 'TODOS OS CARGOS' and sel_turma == "TODAS AS TURMAS":
            detratores = len(av.query("TITULO == @sel_formacao and CARGO_MAT1 == @sel_cargos and Status_NPS == 'Detrator'"))
            neutros = len(av.query("TITULO == @sel_formacao and CARGO_MAT1 == @sel_cargos and Status_NPS == 'Neutro'"))
            promotores = len(av.query("TITULO == @sel_formacao and CARGO_MAT1 == @sel_cargos and Status_NPS == 'Promotor'"))

            inscritos_total = len(inscritos_final.query("TITULO == @sel_formacao and CARGO_MAT1 == @sel_cargos"))
            total = len(av.query("TITULO == @sel_formacao and CARGO_MAT1 == @sel_cargos and Status_NPS != ''"))

            nota_formacao = int(float((format(av.query("TITULO == @sel_formacao and CARGO_MAT1 == @sel_cargos")['Nota da Formação'].mean(),'.0f')))*10)
            nota_aplicacao = int(float((format(av.query("TITULO == @sel_formacao and CARGO_MAT1 == @sel_cargos")['Nota Aplicação'].mean(),'.0f'))) * 10)

            cre_tab = av.query("TITULO == @sel_formacao and CARGO_MAT1 == @sel_cargos and Status_NPS != ''")[['REGIAO_ID_MATRICULA', 'SERVIDOR_ID']]
            inscritos_final_cre = inscritos_final.query("TITULO == @sel_formacao and CARGO_MAT1 == @sel_cargos")[['REGIAO_ID_MATRICULA', 'SERVIDOR_ID']]





        elif sel_formacao != 'TODAS AS FORMAÇÕES' and sel_cargos != 'TODOS OS CARGOS' and sel_turma != "TODAS AS TURMAS":
            detratores = len(av.query("TITULO == @sel_formacao and CARGO_MAT1 == @sel_cargos and Turma == @sel_turma and Status_NPS == 'Detrator'"))
            neutros = len(av.query("TITULO == @sel_formacao and CARGO_MAT1 == @sel_cargos and Turma == @sel_turma and Status_NPS == 'Neutro'"))
            promotores = len(av.query("TITULO == @sel_formacao and CARGO_MAT1 == @sel_cargos and Turma == @sel_turma and Status_NPS == 'Promotor'"))

            inscritos_total = len(inscritos_final.query("TITULO == @sel_formacao and CARGO_MAT1 == @sel_cargos and Turma == @sel_turma"))
            total = len(av.query("TITULO == @sel_formacao and CARGO_MAT1 == @sel_cargos and Turma == @sel_turma and Status_NPS != ''"))

            nota_formacao = int(float((format(av.query("TITULO == @sel_formacao and CARGO_MAT1 == @sel_cargos and Turma == @sel_turma")['Nota da Formação'].mean(), '.0f'))) * 10)
            nota_aplicacao = int(float((format(av.query("TITULO == @sel_formacao and CARGO_MAT1 == @sel_cargos and Turma == @sel_turma")['Nota Aplicação'].mean(), '.0f'))) * 10)

            cre_tab = av.query("TITULO == @sel_formacao and CARGO_MAT1 == @sel_cargos and Turma == @sel_turma and Status_NPS != ''")[['REGIAO_ID_MATRICULA', 'SERVIDOR_ID']]
            inscritos_final_cre = inscritos_final.query("TITULO == @sel_formacao and CARGO_MAT1 == @sel_cargos and Turma == @sel_turma")[['REGIAO_ID_MATRICULA', 'SERVIDOR_ID']]


        elif sel_formacao != 'TODAS AS FORMAÇÕES' and sel_cargos == 'TODOS OS CARGOS' and sel_turma == "TODAS AS TURMAS":
            detratores = len(av.query("TITULO == @sel_formacao and Status_NPS == 'Detrator'"))
            neutros = len(av.query("TITULO == @sel_formacao and Status_NPS == 'Neutro'"))
            promotores = len(av.query("TITULO == @sel_formacao and Status_NPS == 'Promotor'"))

            inscritos_total = len(inscritos_final.query("TITULO == @sel_formacao"))
            total = len(av.query("TITULO == @sel_formacao and Status_NPS !=''"))

            nota_formacao = int(float((format(av.query("TITULO == @sel_formacao")['Nota da Formação'].mean(), '.0f'))) * 10)
            nota_aplicacao = int(float((format(av.query("TITULO == @sel_formacao")['Nota Aplicação'].mean(), '.0f'))) * 10)


            cre_tab = av.query("TITULO == @sel_formacao and Status_NPS !=''")[['REGIAO_ID_MATRICULA', 'SERVIDOR_ID']]
            inscritos_final_cre = inscritos_final.query("TITULO == @sel_formacao")[['REGIAO_ID_MATRICULA', 'SERVIDOR_ID']]


        elif sel_formacao != 'TODAS AS FORMAÇÕES' and sel_cargos == 'TODOS OS CARGOS' and sel_turma != "TODAS AS TURMAS":
            detratores = len(av.query("TITULO == @sel_formacao and Turma == @sel_turma and Status_NPS == 'Detrator'"))
            neutros = len(av.query("TITULO == @sel_formacao and Turma == @sel_turma and Status_NPS == 'Neutro'"))
            promotores = len(av.query("TITULO == @sel_formacao and Turma == @sel_turma and Status_NPS == 'Promotor'"))

            inscritos_total = len(inscritos_final.query("TITULO == @sel_formacao and Turma == @sel_turma"))
            total = len(av.query("TITULO == @sel_formacao and Turma == @sel_turma and Status_NPS !=''"))

            nota_formacao = int(float((format(av.query("TITULO == @sel_formacao and Turma == @sel_turma")['Nota da Formação'].mean(), '.0f'))) * 10)
            nota_aplicacao = int(float((format(av.query("TITULO == @sel_formacao and Turma == @sel_turma")['Nota Aplicação'].mean(), '.0f'))) * 10)

            cre_tab = av.query("TITULO == @sel_formacao and Turma == @sel_turma and Status_NPS !=''")[['REGIAO_ID_MATRICULA', 'SERVIDOR_ID']]
            inscritos_final_cre = inscritos_final.query("TITULO == @sel_formacao and Turma == @sel_turma")[['REGIAO_ID_MATRICULA', 'SERVIDOR_ID']]

        nps_tab = pd.DataFrame({
            'Status': ['Detratores', 'Neutros', 'Promotores'],
            'Servidores': [detratores, neutros, promotores]
        }
        ).reset_index(drop=True)
        nps = (promotores / total - detratores / total) * 100
        nps_valor = int(format(nps, '.0f'))
        r = total / inscritos_total
        razao = format(r, '.2%')
        if r < 0.5:
            txt_conversao = 'Taxa de Conversão = Baixa'
            color = 'normal'
            indicador = format(-0.5, '.1%')
        elif 0.5 < r < 0.75:
            txt_conversao = 'Taxa de Conversão = Intermediária'
            color = 'off'
            indicador = format(+0.5, '.1%')
        elif 0.75 < r:
            txt_conversao = 'Taxa de Conversão = Alta'
            color = 'normal'
            indicador = format(+0.75, '.1%')
        else:
            txt_conversao = 'Taxa de Conversão = Alta'
            color = 'normal'
            indicador = format(+0.75, '.1%')

    with c2:

        st.plotly_chart(go.Figure(go.Indicator(
            mode='number+gauge',
            value=nota_formacao,
            number={'font_size': 40},
            title={'text': 'Nota média da formação:', 'font_size': 20},
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={'axis': {'range': [0, 100]},
                   'bar': {'color': 'aqua'}},
        )).update_layout(width=300, height=200, margin_t=60, margin_b=4
                         ), use_container_width=True)
    with c3:

        st.plotly_chart(go.Figure(go.Indicator(
            mode='number+gauge',
            value=nota_aplicacao,
            number={'font_size':40},
            title={'text': 'Aplicabilidade do conteúdo:', 'font_size': 20},
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={'axis': {'range': [0, 100]},
                   'bar': {'color': 'aqua'}},
        )).update_layout(width=300, height=200, margin_t=60, margin_b=4
                         ),use_container_width=True)

    st.write('---')


    cl1, cl2, cl3 = st.columns(3)
    with cl1:
        st.subheader('NPS da formação')
        if nps_valor < 0:
            st.error('Zona Crítica')
        elif 0 < nps_valor <= 50:
            st.warning('Zona de aperfeiçoamento')
        elif 50 < nps_valor < 75:
            st.info('Zona de qualidade')
        else:
            st.success('Zona de excelência')

        fig = go.Figure(go.Pie(labels=nps_tab['Status'], values=nps_tab['Servidores'], hole=.6))
        fig.update_layout(annotations=[dict(text=nps_valor, x=0.5, y=0.5, font_size=40, showarrow=False)],
                          margin_t=15,
                          margin_b=180,
                          legend=dict(font=dict(size=16))
                          )
        st.plotly_chart(fig, use_container_width=True)

    with cl2:
        st.subheader('Índice de conversão:',help='Porcentagem de avaliações em relação às inscrições. '
                                                 'Se maior que 75%, é alto, entre 50% e 75% é intermediário'
                                                 ' e menor que 50% é baixo.')

        if r*100 < 50:
            st.error('Índice de conversão baixo',  icon='⚠️')
        elif 50 <= r*100 < 75:
            st.info('Índice de conversão intermediário',icon='☑️')
        else:
            st.success('Índice de conversão alto',icon='🌟')

        st.plotly_chart(go.Figure(go.Indicator(
            mode='number',
            value=r*100,
            number={"suffix":"%","font_size":30},
            title= {"text": "Taxa de conversão:","font_size":15}

        )).update_layout(paper_bgcolor = "rgba(100,100,100,0.1)",
                         height = 80,
                         margin_t= 400,
                         margin_b=250,
        ), use_container_width=True)

        st.plotly_chart(go.Figure(go.Indicator(
            mode='number',
            value=inscritos_total,
            number={"font_size":30},
            title= {"text": "Servidores inscritos:","font_size":15}

        )).update_layout(paper_bgcolor = "rgba(100,100,100,0.1)",
                         height = 80,
                         margin_t= 400,
                         margin_b=250,
        ), use_container_width=True)

        st.plotly_chart(go.Figure(go.Indicator(
            mode='number',
            value=total,
            number={"font_size":30},
            title= {"text": "Total de avaliações","font_size":15}

        )).update_layout(paper_bgcolor = "rgba(100,100,100,0.1)",
                         height = 80,
                         margin_t= 400,
                         margin_b=250
        ), use_container_width=True)
    with  cl3:
        st.subheader('Conversão por Região:')
        cre_tab_av = cre_tab.groupby(['REGIAO_ID_MATRICULA']).size().reset_index(name='AVALIAÇÕES')
        cre_tab_av['REGIAO_ID_MATRICULA'].replace(to_replace=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],value=['SEM REGIÃO', '1ªCRE', '2ªCRE', '3ªCRE', '4ªCRE', '5ªCRE', '6ªCRE', '7ªCRE', '8ªCRE','9ªCRE', '10ªCRE', '11ªCRE', 'NÍVEL CENTRAL'], inplace=True)

        inscritos_final_cre = inscritos_final_cre.groupby(['REGIAO_ID_MATRICULA']).size().reset_index(name='INSCRIÇÕES')
        inscritos_final_cre['REGIAO_ID_MATRICULA'].replace(to_replace=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], value=['SEM REGIÃO', '1ªCRE', '2ªCRE', '3ªCRE', '4ªCRE', '5ªCRE', '6ªCRE', '7ªCRE','8ªCRE', '9ªCRE', '10ªCRE', '11ªCRE'], inplace=True)

        cre_final = pd.merge(cre_tab_av, inscritos_final_cre, on='REGIAO_ID_MATRICULA').rename(columns={'REGIAO_ID_MATRICULA':'REGIÃO'})


        trace0 = go.Bar(
            x =cre_final['AVALIAÇÕES'],
            y =cre_final['REGIÃO'],
            name='Avaliações',
            orientation='h'
        )
        trace1 = go.Bar(
            x =cre_final['INSCRIÇÕES'],
            y =cre_final['REGIÃO'],
            name = 'Inscrições',
            orientation='h'
        )
        data = [trace0,trace1]
        layout = go.Layout(
            barmode='group'
        )
        fig = go.Figure(data = data,layout = layout).update_layout(
            width = 400,
            height = 400,
            margin_t=0,
            margin_l = 100,
            legend=dict(
                yanchor="bottom",
                y=0.01,
                xanchor="right",
                x=0.99,
                font=dict(size=16)
            )
        )
        st.plotly_chart(fig)

