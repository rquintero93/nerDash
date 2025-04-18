
    # Create placeholder elements that we can update and clear
    status_placeholder = st.empty()
    progress_placeholder = st.empty()
    
    status_placeholder.write("Analyzing sentiment...")
    progress_bar = progress_placeholder.progress(0)
    
    # Process in batches with progress bar
    batch_size = 32  # Size of each progress update batch
    results = []
    
    for i in range(0, len(descriptions), batch_size):
        batch = descriptions[i:i+batch_size]
        batch_results = sentiment_pipeline(batch)
        results.extend(batch_results)
        progress_placeholder.progress(min(1.0, (i + batch_size) / len(descriptions)))
    # Sort edges by weight (highest first) and take only the top max_edges
    status_placeholder.write(f"Found {len(all_edges)} edges, sorting and adding top {max_edges}...")
    all_edges.sort(key=lambda x: x[2], reverse=True)
    
    # Add the top edges to the graph
    for idx, (i, j, score) in enumerate(all_edges[:max_edges]):
        G.add_edge(i, j, weight=score)
        if idx % max(1, max_edges // 50) == 0:  # Update every 2%
            progress_placeholder.progress(min(1.0, 0.9 + (0.1 * idx / min(len(all_edges), max_edges))))
    
    # Clear placeholders when done
    status_placeholder.empty()
    progress_placeholder.empty()
