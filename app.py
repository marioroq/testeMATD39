import streamlit as st

st.title("Primeiro App")

st.header("Cabeçalho do Site")

n = st.number_input("Digite um número: ")

st.write(f"Seu número é {(n**2)/2}")