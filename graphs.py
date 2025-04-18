
    # Create placeholder elements
    status_placeholder = st.empty()
    progress_placeholder = st.empty()
    
    status_placeholder.write("Creating graph visualization...")
    progress_placeholder.progress(0)
    
    # Limit to largest connected component if graph is too large
    if len(G.nodes()) > 200:
