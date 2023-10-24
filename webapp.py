import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
import os 
import warnings

def calc_carbon_rating(electricity_consumption, oil_consumption, transportation_consumption):
    max_electricity = 10000  
    max_oil = 10000  
    max_transportation = 10000 

    normalized_electricity = electricity_consumption / max_electricity
    normalized_oil = oil_consumption / max_oil
    normalized_transportation = transportation_consumption / max_transportation

    weight_electricity = 0.5
    weight_oil = 0.25
    weight_transportation = 0.25

    unbounded_score = (
        weight_electricity * normalized_electricity +
        weight_oil * normalized_oil +
        weight_transportation * normalized_transportation
    )

    min_unbounded = 1 
    max_unbounded = 5  

    carbon_rating = 1 + 4 * ((unbounded_score - min_unbounded) / (max_unbounded - min_unbounded))
    return carbon_rating


warnings.filterwarnings('ignore')

st.set_page_config(page_title = "Amazon Supply Chain Management", page_icon = ":baggage_claim", layout = "wide")
st.title(" :baggage_claim: Supply Chain DashBoard")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>',unsafe_allow_html=True)



fl2 = st.file_uploader(":file_folder: Electricity Consumption Data",type=(["csv","txt","xlsx","xls"]))
if fl2 is not None:
    filename = fl2.name
    st.write(filename)
    df2 = pd.read_csv(filename, encoding='latin-1')
    d1, d2 = st.columns((2))
    with d1:
        cd1, cd2 = st.columns((2))
        df2['datetime'] = pd.to_datetime(df2['datetime'])
        startDate = pd.to_datetime(df2['datetime']).min()
        endDate = pd.to_datetime(df2['datetime']).max()

        with cd1:
            date1 = pd.to_datetime(st.date_input("Start Date", startDate))

        with cd2:
            date2 = pd.to_datetime(st.date_input("End Date", endDate))

        df2 = df2[(df2["datetime"] >= date1) & (df2["datetime"] <= date2)].copy()
        st.subheader(':electric_plug: Electricity Trends')
        st.line_chart(df2, x="datetime", y="consumption", color="#ffaa00")
    with d2:
        st.subheader(":four_leaf_clover: Calculate Carbon Footprint")

        el  = df2["consumption"].mean()
        el_calc= el * 105
        gas = st.number_input('Enter Gas Bill Rupees/Per Meter Cube')
        gas_calc = gas * 105
        oil = st.number_input('Enter Oil Bill Rupees/Per Litre')
        oil_calc = oil * 113
        carbon_footprint = el_calc + gas_calc + oil_calc
        carbon_footprint = round(carbon_footprint/10, 2)
        # cd1, cd2 = st.columns((2))
        if st.button('Calculate'):
                st.text(f"Carbon Footprint: {(carbon_footprint)} kg CO2")
                carbon_rating = calc_carbon_rating(el, gas, oil)
                carbon_rating = carbon_rating * 10
                carbon_rating = round(carbon_rating,2) 
                carbon_rating = 5 - carbon_rating
                st.text(f"Carbon Rating:") 
                carbon_rating
                if carbon_rating <= 2 or carbon_footprint > 15000:
                    st.caption(":x: Bad")
                elif carbon_rating > 2 and carbon_rating < 4 or carbon_footprint < 15000 and carbon_footprint > 6000:
                    st.caption(":neutral_face: Neutral")
                elif carbon_rating <= 5 or carbon_footprint <= 6000:
                    st.caption(":white_check_mark: Good")

        
    # d3, d4, d5 = st.columns((3))
    # with d3:
    #     st.subheader(':seedling:   Your Carbon Rating')
    # with d4:
    #     st.subheader('Manage Electric Trends')
    # with d5:
    #     st.subheader('Manage Electric Trends')
        
fl = st.file_uploader(":file_folder: Upload Supply Chain Data Set",type=(["csv","txt","xlsx","xls"]))
if fl is not None:
    filename = fl.name
    st.write(filename)
    df = pd.read_csv(filename, encoding='latin-1')

    col1, col2 = st.columns((2))
    df['order date (DateOrders)'] = pd.to_datetime(df['order date (DateOrders)'])
    startDate = pd.to_datetime(df['order date (DateOrders)']).min()
    endDate = pd.to_datetime(df['order date (DateOrders)']).max()

    with col1:
        date1 = pd.to_datetime(st.date_input("Start Date", startDate))

    with col2:
        date2 = pd.to_datetime(st.date_input("End Date", endDate))

    df = df[(df["order date (DateOrders)"] >= date1) & (df["order date (DateOrders)"] <= date2)].copy()
    st.sidebar.header("Add Filter: ")

    region = st.sidebar.multiselect("Pick your Region", df["Market"].unique())
    if not region:
        df2 = df.copy()
    else:
        df2 = df[df["Market"].isin(region)]

    # Create for State
    state = st.sidebar.multiselect("Pick the State", df2["Customer State"].unique())
    if not state:
        df3 = df2.copy()
    else:
        df3 = df2[df2["Customer State"].isin(state)]

    # Create for City
    city = st.sidebar.multiselect("Pick the City",df3["Customer City"].unique())

    if not region and not state and not city:
        filtered_df = df
    elif not state and not city:
        filtered_df = df[df["Market"].isin(region)]
    elif not region and not city:
        filtered_df = df[df["Customer State"].isin(state)]
    elif state and city:
        filtered_df = df3[df["Customer State"].isin(state) & df3["Customer City"].isin(city)]
    elif region and city:
        filtered_df = df3[df["Market"].isin(region) & df3["Customer City"].isin(city)]
    elif region and state:
        filtered_df = df3[df["Market"].isin(region) & df3["Customer State"].isin(state)]
    elif city:
        filtered_df = df3[df3["Customer City"].isin(city)]
    else:
        filtered_df = df3[df3["Market"].isin(region) & df3["Customer State"].isin(state) & df3["Customer City"].isin(city)]

    category_df = filtered_df.groupby(by = ["Category Name"], as_index = False)["Sales"].sum()

    with col1:
        st.subheader("Category wise Supplies")
        fig = px.bar(category_df, x = "Category Name", y = "Sales", text = ['${:,.2f}'.format(x) for x in category_df["Sales"]],
                    template = "seaborn")
        st.plotly_chart(fig,use_container_width=True, height = 200)

    with col2:
        st.subheader("Region wise Supplies")
        fig = px.pie(filtered_df, values = "Sales", names = "Market", hole = 0.5)
        fig.update_traces(text = filtered_df["Market"], textposition = "outside")
        st.plotly_chart(fig,use_container_width=True)

    st.subheader('Time Series Analysis')
    filtered_df["month_year"] = filtered_df["order date (DateOrders)"].dt.to_period("M")
    linechart = pd.DataFrame(filtered_df.groupby(filtered_df["month_year"].dt.strftime("%Y : %b"))["Sales"].sum()).reset_index()
    fig2 = px.line(linechart, x = "month_year", y="Sales", labels = {"Sales": "Order Item Product Price"},height=500, width = 1000,template="gridon")
    st.plotly_chart(fig2,use_container_width=True)


    # Create a treem based on Region, category, sub-Category
    st.subheader("Hierarchical view of Sales using TreeMap")
    fig3 = px.treemap(filtered_df, path = ["Market","Category Name"], values = "Sales",hover_data = ["Sales"],
                    color = "Category Name")
    fig3.update_layout(width = 800, height = 650)
    st.plotly_chart(fig3, use_container_width=True)

    chart1, chart2 = st.columns((2))
    with chart1:
        st.subheader('Segment wise Sales')
        fig = px.pie(filtered_df, values = "Sales", names = "Market", template = "plotly_dark")
        fig.update_traces(text = filtered_df["Market"], textposition = "inside")
        st.plotly_chart(fig,use_container_width=True)

    with chart2:
        st.subheader('Category wise Sales')
        fig = px.pie(filtered_df, values = "Sales", names = "Category Name", template = "gridon")
        fig.update_traces(text = filtered_df["Category Name"], textposition = "inside")
        st.plotly_chart(fig,use_container_width=True)

    import plotly.figure_factory as ff
    st.subheader(":point_right: Month wise Sub-Category Sales Summary")
    with st.expander("Summary_Table"):
        df_sample = df[0:5][["Market","Customer State","Customer City","Category Name","Sales","Order Profit Per Order","Order Item Quantity"]]
        fig = ff.create_table(df_sample, colorscale = "Cividis")
        st.plotly_chart(fig, use_container_width=True)


    # scatter plot
    data1 = px.scatter(filtered_df, x = "Sales", y = "Order Profit Per Order", size = "Order Item Quantity")
    data1['layout'].update(
        title="Relationship between Sales and Profits using Scatter Plot.",
        titlefont = dict(size=20),
        xaxis = dict(title="Sales",
        titlefont=dict(size=19)),
        yaxis = dict(title = "Profit", titlefont = dict(size=19)))
    st.plotly_chart(data1,use_container_width=True)

cmain1, cmain2, cmain3 = st.columns((3))
with cmain1:
    # st.subheader('Explore Other Amazon Products')
    centered_div = """
    <div style="
            display: flex; 
            flex-direction: column; 
            align-items: center; 
            text-align: center;
        ">
        <h2 style="margin-bottom: 20px;">Explore Other Amazon Products</h2>
        <h4 style="margin-bottom: 20px; font-weight: 50; font-size: 100%;">  
                Amazon offers a diverse range of products beyond e-commerce, including Amazon Web Services (AWS), Amazon Prime Video, and Amazon Echo, making it a multifaceted tech giant.
            </h4>
        <button 
            style="width: 200px; 
            padding: 10px; 
            background-color: #ffaa00; 
            border: none; 
            border-radius: 5px;
        ">Explore Amazon</button>
    </div>
    """

    st.markdown(centered_div, unsafe_allow_html=True)

with cmain2:
    centered_div = """
    <div style="
            display: flex; 
            flex-direction: column; 
            align-items: center; 
            text-align: center;
        ">
        <h2 style="margin-bottom: 20px;">Explore Carbon Points and Credits</h2>
        <h4 style="margin-bottom: 20px; font-weight: 100; font-size: 100%;"> 
                System to incentivize individuals and organizations to reduce their carbon footprint by rewarding eco-friendly actions and can play a crucial role in combating climate change.
            </h4>
        <button 
            style="width: 200px; 
            padding: 10px; 
            background-color: #ffaa00; 
            border: none; 
            border-radius: 5px;
        ">Explore Carbon Points</button>
    </div>
    """
    st.markdown(centered_div, unsafe_allow_html=True)

with cmain3:
    centered_div = """
    <div style="
            display: flex; 
            flex-direction: column; 
            align-items: center; 
            text-align: center;
        ">
        <h2 style="margin-bottom: 20px;">
                Explore Carbon Neutral Projects 
            </h2> 
        <h4 style="margin-bottom: 20px; font-weight: 100; font-size: 100%;"> 
                Carbon neutral projects aim to reduce or offset greenhouse gas emissions to achieve a net-zero carbon footprint, contributing to a more sustainable and environmentally friendly future.
            </h4>
        <button 
            style="width: 200px; 
            padding: 10px; 
            background-color: #ffaa00; 
            border: none; 
            border-radius: 5px;
            transition: background-color 0.3s ease; 
        "
        >Explore Carbon Market</button>
    </div>
    """

    st.markdown(centered_div, unsafe_allow_html=True)
