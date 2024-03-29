import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime
import calendar

def main():
    st.image("GDI.jpg", width=720)
    st.sidebar.title("Instrucciones")
    st.sidebar.write("¡Bienvenido a la aplicación de gerenciamiento diario!")
    st.sidebar.markdown("Por favor sigue las instrucciones paso a paso para utilizar la herramienta correctamente.")
    
    st.sidebar.markdown("### Pasos:")
    st.sidebar.markdown("- **Paso 1:** Ingresa el indicador clave.")
    st.sidebar.markdown("- **Paso 2:** Establece la meta para el indicador.")
    st.sidebar.markdown("- **Paso 3:** Define si el indicador es 'Mejor Menor' o 'Mejor Mayor'.")
    st.sidebar.markdown("- **Paso 4:** Ingresa el resultado diario para el indicador.")
    st.sidebar.markdown("- **Paso 5:** Observa el gráfico de control respecto a la meta.")
    st.sidebar.markdown("- **Paso 6:** Analiza el desempeño diario del indicador.")
    
    st.sidebar.markdown("### Información Adicional:")
    st.sidebar.markdown("👉 **Para más información: [LinkedIn](https://www.linkedin.com/in/josemaguilar/)**")
    
    # Configuración de los indicadores clave
    indicators = []
    for i in range(3):
        st.sidebar.title(f"Configuración del Indicador Clave {i+1}")
        indicator_name = st.sidebar.text_input(f"Nombre del Indicador {i+1}:")
        target = st.sidebar.number_input(f"Meta para el Indicador {i+1}:", step=0.01)
        is_better_lower = st.sidebar.radio(f"Mejor cuando para el Indicador {i+1}:", ("Menor que la meta", "Mayor que la meta"))
        indicators.append((indicator_name, target, is_better_lower))

    # Ingreso de resultados diarios para cada indicador
    first_day_of_month_input = st.sidebar.date_input("Ingrese el primer día del mes:", value=datetime.now().replace(day=1))
    num_days_in_month = calendar.monthrange(first_day_of_month_input.year, first_day_of_month_input.month)[1]

    daily_results = [[] for _ in range(3)]
    cause_columns = [[] for _ in range(3)]

    # Iterar sobre los días y los indicadores para ingresar los resultados diarios
    for day in range(num_days_in_month):
        for i in range(3):
            st.sidebar.title(f"Indicador {i+1}: {indicators[i][0]}")
            date = first_day_of_month_input.replace(day=day + 1)  # Sumar 1 para evitar el índice 0
            day_of_week = date.strftime("%A")  # Obtener el nombre del día de la semana
            daily_result = st.sidebar.number_input(f"Ingrese el resultado del día {day+1} para el Indicador {i+1} ({date.strftime('%d/%m/%Y')} - {day_of_week}):", key=f"daily_result_{day}_{i}", step=0.01)
            daily_results[i].append(daily_result)
            
            if daily_result < indicators[i][1]:
                cause_columns[i].append(st.sidebar.selectbox(f"Causas para el día {day+1} para el Indicador {i+1} ({date.strftime('%d/%m/%Y')} - {day_of_week}):", key=f"cause_columns_{day}_{i}", options=[" ","Materiales", "Métodos", "Maquinaria", "Mano de obra", "Medio ambiente", "Medición"]))
            else:
                cause_columns[i].append(None)


    # Crear DataFrame para cada indicador
    data_dfs = []
    for i in range(3):
        data_df = pd.DataFrame({"Día": [first_day_of_month_input.replace(day=day+1) for day in range(num_days_in_month)], f"Resultado {i+1} - {indicators[i][0]}": daily_results[i]})
        causas = [cause_columns[i][day] if daily_results[i][day] < indicators[i][1] else None for day in range(num_days_in_month)]
        data_df["Causas"] = causas
        data_dfs.append(data_df)

    # Mostrar los gráficos en las columnas
    #st.subheader("Seguimiento diario")
    col1, col2, col3 = st.columns(3)
    for i in range(3):
        if not data_dfs[i].empty:
            target = indicators[i][1]
            is_better_lower = indicators[i][2]
            
            # Filtrar valores en 0 antes de calcular el promedio
            non_zero_values = data_dfs[i][f"Resultado {i+1} - {indicators[i][0]}"][data_dfs[i][f"Resultado {i+1} - {indicators[i][0]}"] != 0]
            mean_result = non_zero_values.mean()
            
            cumplimiento = mean_result >= target if is_better_lower == "Menor que la meta" else mean_result <= target
            
            # Crear Gauge Chart
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = mean_result,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': f"{indicators[i][0]}"},
                gauge = {'axis': {'range': [None, max(non_zero_values.max(), target)]},
                         'bar': {'color': "red" if cumplimiento else "green"},
                         'steps' : [
                             {'range': [0, target], 'color': "lightblue"}],
                         'threshold' : {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': target}}))

            fig_gauge.update_layout(height=250, width=220)

            # Crear Control Chart
            fig_control = go.Figure()
            if f"Resultado {i+1} - {indicators[i][0]}" in data_dfs[i].columns:
                non_zero_data = data_dfs[i][data_dfs[i][f"Resultado {i+1} - {indicators[i][0]}"] != 0]  # Filtrar valores diferentes de cero
                colors = ['red' if r > target and is_better_lower == "Menor que la meta" or r < target and is_better_lower == "Mayor que la meta" else 'green' for r in non_zero_data[f"Resultado {i+1} - {indicators[i][0]}"]]
                fig_control.add_trace(go.Scatter(x=non_zero_data["Día"], y=non_zero_data[f"Resultado {i+1} - {indicators[i][0]}"], mode='markers', marker=dict(color=colors, size=10), name='Resultado Diario'))
                fig_control.add_hline(y=target, line_dash="dash", line_color="black", annotation_text="Meta", annotation_position="top right")
                fig_control.add_trace(go.Scatter(x=non_zero_data["Día"], y=non_zero_data[f"Resultado {i+1} - {indicators[i][0]}"], mode='lines', line=dict(color='blue'), name='Tendencia Diaria'))
                fig_control.update_layout(title=f'Desempeño de {indicators[i][0]}',
                                        xaxis_title='Día',
                                        yaxis_title='Resultado',
                                        showlegend=False)

            fig_control.update_layout(height=350, width=220)

            # Crear Gráfico de Barras para Causas
            if "Causas" in data_dfs[i].columns:
                causas_filtradas = data_dfs[i]["Causas"].value_counts().sort_values(ascending=False)
                
                # Filtrar valores diferentes de " " o seleccionados
                causas_filtradas = causas_filtradas[causas_filtradas.index != " "]
                
                fig_causas = go.Figure(go.Bar(
                    x=causas_filtradas.values,
                    y=causas_filtradas.index,
                    orientation='h'
                ))
                fig_causas.update_layout(title=f'Causas para {indicators[i][0]}',
                                        xaxis_title='Frecuencia',
                                        yaxis_title='Causas',
                                        yaxis=dict(autorange="reversed"),
                                        showlegend=False)
                fig_causas.update_layout(height=350, width=240)

            # Crear Gráfico de Calendario
            fig_calendar = go.Figure()
            calendar_data = {}
            for _, row in data_dfs[i].iterrows():
                week_of_year = row['Día'].isocalendar()[1]
                if week_of_year not in calendar_data:
                    calendar_data[week_of_year] = [None] * 7
                day_of_week = row['Día'].weekday()
                if row[f"Resultado {i+1} - {indicators[i][0]}"] == 0:
                    calendar_data[week_of_year][day_of_week] = None  # Valor en blanco
                elif row[f"Resultado {i+1} - {indicators[i][0]}"] <= target and is_better_lower == "Menor que la meta":
                    calendar_data[week_of_year][day_of_week] = 1  # Valor en verde
                elif row[f"Resultado {i+1} - {indicators[i][0]}"] >= target and is_better_lower == "Mayor que la meta":
                    calendar_data[week_of_year][day_of_week] = 1   # Valor en verde
                else:
                    calendar_data[week_of_year][day_of_week] = -1  # Valor en rojo

            for week_of_year, data in calendar_data.items():
                fig_calendar.add_trace(go.Heatmap(
                    z=[data],
                    x=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
                    y=[f'Semana {week_of_year}'],
                    colorscale=[[0, 'red'], [0.5, 'white'], [1, 'green']],  # Personaliza la escala de colores
                    zmin=-1,  # Valor mínimo personalizado
                    zmax=1,   # Valor máximo personalizado
                    colorbar=dict(showticklabels=False)
                ))

            fig_calendar.update_layout(title=f'{indicators[i][0]} - Cump. diario',
                                       xaxis_title='Día de la Semana',
                                       yaxis_title='Semana del Año',
                                       yaxis=dict(autorange="reversed"),
                                       yaxis_showticklabels=False)  # Oculta los nombres de las semanas en el eje Y
            fig_calendar.update_layout(height=350, width=250)

            if i == 0:
                with col1:
                    st.plotly_chart(fig_gauge)
                    st.plotly_chart(fig_control)
                    st.plotly_chart(fig_causas)
                    st.plotly_chart(fig_calendar)
                    st.write(f"{indicators[i][0]}")  # Mostrar el título del indicador
                    st.dataframe(data_dfs[i])  # Mostrar el DataFrame del indicador
            elif i == 1:
                with col2:
                    st.plotly_chart(fig_gauge)
                    st.plotly_chart(fig_control)
                    st.plotly_chart(fig_causas)
                    st.plotly_chart(fig_calendar)
                    st.write(f"{indicators[i][0]}")  # Mostrar el título del indicador
                    st.dataframe(data_dfs[i])  # Mostrar el DataFrame del indicador
            elif i == 2:
                with col3:
                    st.plotly_chart(fig_gauge)
                    st.plotly_chart(fig_control)
                    st.plotly_chart(fig_causas)
                    st.plotly_chart(fig_calendar)
                    st.write(f"{indicators[i][0]}")  # Mostrar el título del indicador
                    st.dataframe(data_dfs[i])  # Mostrar el DataFrame del indicador

if __name__ == "__main__":
    main()


