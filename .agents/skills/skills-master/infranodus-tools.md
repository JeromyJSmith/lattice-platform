Title: InfraNodus MCP Tools: Complete Descriptions & Examples

URL Source: http://infranodus.com/mcp/tools

Markdown Content:
Below you will find descriptions of every tool available in the InfraNodus MCP, its typical use case, the data it receives, and the structure of the response generated.

You can also use the tools with URL links (including YouTube videos which will be automatically transcribed) as well as existing InfraNodus graphs.

Note that exact schemas may change, so it's better to avoid hard-coding tool names or fields and instead rely on your LLM reading through all available tool descriptions.

#### Available Tools

**Analysis Tools**

*   [generate_knowledge_graph](http://infranodus.com/mcp/tools#generate_knowledge_graph) — Generate a knowledge graph from text with full structural analysis
*   [create_knowledge_graph](http://infranodus.com/mcp/tools#create_knowledge_graph) — Create and save a knowledge graph in InfraNodus
*   [generate_topical_clusters](http://infranodus.com/mcp/tools#generate_topical_clusters) — Extract topical clusters from text
*   [generate_content_gaps](http://infranodus.com/mcp/tools#generate_content_gaps) — Identify content gaps in discourse
*   [generate_research_questions](http://infranodus.com/mcp/tools#generate_research_questions) — Generate questions bridging content gaps
*   [generate_research_ideas](http://infranodus.com/mcp/tools#generate_research_ideas) — Generate innovative ideas from content gaps
*   [generate_contextual_hint](http://infranodus.com/mcp/tools#generate_contextual_hint) — Structural summary for GraphRAG augmentation
*   [analyze_existing_graph_by_name](http://infranodus.com/mcp/tools#analyze_existing_graph_by_name) — Analyze an existing InfraNodus graph
*   [analyze_text](http://infranodus.com/mcp/tools#analyze_text) — General text analysis with diversity insights

**Development Tools**

*   [develop_latent_topics](http://infranodus.com/mcp/tools#develop_latent_topics) — Identify and develop underdeveloped topics
*   [develop_conceptual_bridges](http://infranodus.com/mcp/tools#develop_conceptual_bridges) — Find concepts that bridge to broader discourse
*   [develop_text_tool](http://infranodus.com/mcp/tools#develop_text_tool) — Comprehensive text development combining multiple tools
*   [optimize_text_structure](http://infranodus.com/mcp/tools#optimize_text_structure) — Optimize text based on structural analysis

**Utility Tools**

*   [retrieve_from_knowledge_base](http://infranodus.com/mcp/tools#retrieve_from_knowledge_base) — GraphRAG retrieval from existing graphs
*   [list_graphs](http://infranodus.com/mcp/tools#list_graphs) — List user's graphs with filters
*   [search](http://infranodus.com/mcp/tools#search) — Search statements across graphs
*   [fetch](http://infranodus.com/mcp/tools#fetch) — Fetch specific search results

**Memory Tools**

*   [memory_add_relations](http://infranodus.com/mcp/tools#memory_add_relations) — Save knowledge graph memories
*   [memory_get_relations](http://infranodus.com/mcp/tools#memory_get_relations) — Retrieve memories for entities

**Text Comparison Tools**

*   [difference_between_texts](http://infranodus.com/mcp/tools#difference_between_texts) — Find what's missing in text A vs. others
*   [overlap_between_texts](http://infranodus.com/mcp/tools#overlap_between_texts) — Find common topics across texts
*   [merged_graph_from_texts](http://infranodus.com/mcp/tools#merged_graph_from_texts) — Merge multiple texts into one graph

**Google / SEO Tools**

*   [analyze_google_search_results](http://infranodus.com/mcp/tools#analyze_google_search_results) — Graph of Google search results
*   [analyze_related_search_queries](http://infranodus.com/mcp/tools#analyze_related_search_queries) — Analyze search intent
*   [search_queries_vs_search_results](http://infranodus.com/mcp/tools#search_queries_vs_search_results) — Find what people search for but don't find
*   [generate_seo_report](http://infranodus.com/mcp/tools#generate_seo_report) — Full SEO optimization report

## Analysis Tools

generate_knowledge_graph

Generates a knowledge graph from text, URL (including YouTube video), or an existing InfraNodus graph. Shows main concepts (nodes), relations, topical clusters, and gaps. Useful for providing additional reproducible structure to LLMs or to steer their attention to a certain aspect of text.

###### Parameters

`{ "text": "Your text to analyze", "includeGraph": true }`

JSON

###### Response (abbreviated)

```
{
  "statistics": { "modularity": 0.295, "clusterCount": 3, "nodeCount": 14,
    "diversity_stats": { "diversity_score": "focused", "modularity_score": "medium",
      "too_focused_on_top_nodes": true, "ratio_of_top_nodes_influence_by_betweenness": 0.63 }},
  "contentGaps": ["Gap 1: Forbidden Knowledge -> Moral Duality", "..."],
  "mainTopicalClusters": [
    "1. Divine Consumption: god eat eye open (0 | 29% | 63%)",
    "2. Forbidden Knowledge: serpent tree fruit woman midst garden touch (1 | 50% | 26%)",
    "3. Moral Duality: knowing good evil (2 | 21% | 10%)"],
  "mainConcepts": ["god", "eat", "serpent", "knowing", "tree", "good", "..."],
  "conceptualGateways": ["god", "eat", "serpent", "good", "knowing", "..."],
  "topRelations": ["1) god <-> eat", "2) god <-> eye", "3) god <-> open", "..."],
  "topInfluentialNodes": [{ "node": "god", "bc": 0.59, "degree": 11 }],
  "knowledgeGraphByCluster": { "0": ["god <-> eat [label=\"eye, open\"]"], "..." : "..." }
}
```

JSON

create_knowledge_graph

Create a knowledge graph from text or URL and save it in InfraNodus for future reference or as a knowledge base.

###### Parameters

`{ "graphName": "bible_genesis", "text": "Your text here", "includeGraph": true }`

JSON

###### Response

Same as `generate_knowledge_graph` plus: `graphName`, `graphUrl` (link to edit the graph in InfraNodus).

generate_topical_clusters

Extracts topical clusters from text, URL, YouTube video, or an existing graph. Compact delivery of the most important topics. Useful for generating summaries and improving LLM reasoning workflows.

###### Parameters

`{ "text": "Your text to analyze" }`

JSON

###### Response

```
{
  "topicalClusters": [
    "1. Divine Consumption: god eat eye open (0 | 29% | 63%)",
    "2. Forbidden Knowledge: serpent tree fruit woman midst garden touch (1 | 50% | 26%)",
    "3. Moral Duality: knowing good evil (2 | 21% | 10%)" ]
}
```

JSON

generate_content_gaps

Identifies areas of discourse that could be further developed and potential opportunities for generating insights by linking topics that are not well connected.

###### Parameters

`{ "text": "Your text to analyze" }`

JSON

###### Response

```
{
  "contentGaps": [
    "Gap 1: 2. Forbidden Knowledge (...) -> 3. Moral Duality (...)",
    "Gap 2: 1. Divine Consumption (...) -> 2. Forbidden Knowledge (...)",
    "Gap 3: 1. Divine Consumption (...) -> 3. Moral Duality (...)" ]
}
```

JSON

generate_research_questions

Generates research questions that bridge content gaps found in text. Use `useSeveralGaps` for diverse range of questions and `gapDepth` for less prominent gaps.

###### Parameters

`{ "text": "Your text", "useSeveralGaps": true, "modelToUse": "gpt-4o" }`

JSON

###### Response

```
{
  "questions": [
    "How does the interplay between forbidden knowledge and moral duality reflect on contemporary ethical dilemmas...?",
    "How does the act of consuming forbidden fruit symbolize a shift from divine control to human agency...?",
    "How does the metaphor of 'divine consumption' explore the interplay between forbidden knowledge and moral duality...?" ]
}
```

JSON

generate_research_ideas

Generates ideas to develop text further. By default bridges content gaps within the text's context. With `shouldTranscend: true`, focuses on the least represented clusters and conceptual gateways to link the text to a wider discourse.

###### Parameters

`{ "text": "Your text", "useSeveralGaps": true, "shouldTranscend": true, "modelToUse": "gpt-4o" }`

JSON

###### Response

```
{
  "responses": ["In the labyrinth of divine prohibition and serpentine temptation, one might propose a novel perspective: 'Consciousness as the forbidden fruit.'..."]
}
```

JSON

generate_contextual_hint

Generates a structural summary for an LLM to have a general overview of the context. Useful for GraphRAG-augmented retrieval where the system can understand the knowledge base's main topical clusters, concepts, and gaps.

###### Parameters

`{ "text": "Your text to analyze" }`

JSON

###### Response

Returns a `textOverview` string containing structured XML-like tags for MainConcepts, MainTopics, TopicalGaps, ConceptualGateways, Relations, and DiversityStatistics.

analyze_existing_graph_by_name

Extract an existing graph from InfraNodus and provide full graph analysis: main topical clusters, concepts, gaps, and diversity statistics.

###### Parameters

`{ "graphName": "my-graph-name" }`

JSON

###### Response

Same structure as `generate_knowledge_graph` response.

analyze_text

General text analysis from text, URL, or YouTube video. Similar to `generate_knowledge_graph` but focused on analysis results and structural recommendations (e.g. diversity and focus). Includes analyzed statements.

###### Parameters

`{ "text": "Your text to analyze" }`

JSON

###### Response

Same structure as `generate_knowledge_graph` plus `statements` array with content, community assignments, and hashtags.

## Development Tools

develop_latent_topics

Identifies underdeveloped topics and generates ideas (with `requestMode: "transcend"`) or research questions to develop them further. Provides information about the latent topical clusters used.

###### Parameters

`{ "text": "Your text", "requestMode": "transcend" }`

JSON

###### Response

```
{
  "ideas": ["The narrative suggests a deeper exploration: the interplay between forbidden insight and transformative agency..."],
  "mainTopics": ["1. Divine Consumption: god eat eye open (0 | 29% | 63%)", "..."],
  "latentTopicsToDevelop": ["god <-> eat [label=\"eye, open\"]", "..."]
}
```

JSON

develop_conceptual_bridges

Similar to `develop_latent_topics` but focuses on nodes with high ratio of influence to degree (betweenness centrality / degree). These concepts link different topical clusters and can connect the discourse to another context. Useful for thinking "outside the box".

###### Parameters

`{ "text": "Your text", "requestMode": "transcend" }`

JSON

###### Response

```
{
  "ideas": ["The true transformation lies not in forbidden knowledge or divine consumption, but in transcending both..."],
  "latentConceptsToDevelop": ["god", "eat", "serpent", "good", "knowing", "..."],
  "latentConceptsRelations": ["god <-> eat [label=\"woman, fruit, serpent, tree\"]", "..."]
}
```

JSON

develop_text_tool

Comprehensive text development combining multiple tools: (1) "optimize" — generates ideas based on gap between clusters adapting to text structure; (2) "latent" — extracts underdeveloped topics; (3) "conceptual bridges" — extracts concepts linking to broader context. Use `transcendDiscourse: true` to push beyond the text.

###### Parameters

`{ "text": "Your text to develop", "transcendDiscourse": true }`

JSON

###### Response

```
{
  "contentGapIdeas": ["What if the true essence of the garden lies not in avoiding temptation..."],
  "latentTopicsIdeas": ["The narrative suggests a deeper exploration..."],
  "conceptualBridgesIdeas": ["One could propose a novel perspective: the act of 'eating' symbolizes transcendence..."],
  "contentGaps": ["Gap 1: ...", "Gap 2: ...", "Gap 3: ..."],
  "conceptualBridges": ["god", "eat", "serpent", "good", "knowing", "..."],
  "latentTopics": ["god <-> eat [label=\"eye, open\"]", "..."],
  "mainTopics": ["1. Divine Consumption: god eat eye open (0 | 29% | 63%)", "..."]
}
```

JSON

optimize_text_structure

Analyzes bias and coherence in text: if too biased, develops least represented topics; if focused/diversified, develops content gaps; if dispersed, develops most common gap topics. Set `responseType: "transcend"` to connect to wider context.

###### Parameters

`{ "text": "Your text to optimize", "responseType": "transcend" }`

JSON

###### Response

```
{
  "suggestions": ["The narrative contains a dynamic tension between forbidden touch and divine knowledge..."],
  "diversity_stats": { "diversity_score": "focused", "modularity_score": "medium", "..." : "..." },
  "mainTopicalClusters": ["1. Divine Consumption: ...", "2. Forbidden Touch: ...", "3. Moral Awareness: ..."],
  "contentGaps": ["..."],
  "topicsToDevelop": ["midst <-> garden [label=\"...\"]", "knowing <-> good [label=\"evil\"]"],
  "conceptualGateways": ["god", "eat", "serpent", "good", "knowing", "..."]
}
```

JSON

## Utility Tools

retrieve_from_knowledge_base

Get an existing graph by name and retrieve statements relevant to the prompt using GraphRAG and RAG retrieval. Use `includeGraphSummary: true` to augment your RAG flows with contextual overview. Even queries with terms not in the graph (e.g. "sin" for a Bible graph) will retrieve relevant content.

###### Parameters

`{ "graphName": "test_bible", "prompt": "sin", "includeGraphSummary": true }`

JSON

###### Response

```
{
  "retrievedStatements": [
    { "content": "God said, 'You shall not eat of the fruit...'",
      "topStatementCommunity": "1", "similarityScore": 0.167 }
  ],
  "graphSummary": ": god (11 | 0.5897)... ..."
}
```

JSON

list_graphs

Lists all graphs in the user's account. Can search by name, type, date, language, and favorites.

###### Parameters

`{ "nameContains": "bible", "type": "memory" }`

JSON

###### Response

```
{
  "totalGraphs": 1,
  "graphs": [{ "id": 294, "name": "test_bible_memory", "type": "MEMORY",
    "isFavorite": false, "createdAt": "2026-02-14T18:00:31.564Z", "language": "AUTO" }]
}
```

JSON

search

Find all statements in the user's account containing a search term. Required for MCP connections to ChatGPT.

###### Parameters

`{ "query": "serpent" }`

JSON

###### Response

```
{
  "results": [
    { "id": "deemeetree:test_bible:serpent", "title": "test_bible",
      "url": "https://infranodus.com/deemeetree/test_bible/edit" }
  ]
}
```

JSON

fetch

Fetches the statements found using the `search` tool above using the ID it provided.

###### Parameters

`{ "id": "deemeetree:test_bible:serpent" }`

JSON

###### Response

```
{
  "id": "deemeetree:test_bible:serpent", "title": "test_bible",
  "text": "God said, 'You shall not eat of the fruit...'",
  "url": "https://infranodus.com/deemeetree/test_bible/edit"
}
```

JSON

## Memory Tools

InfraNodus has tools for generating "memories" as knowledge graphs. Entities in text are converted to [[wikilinks]] nodes. Useful for saving and retrieving structured memories from LLM conversations.

memory_add_relations

Add relations to a memory graph (creates a new graph if it doesn't exist). By default, entities are detected as [[wikilinks]], so the resulting graph is a high-level representation of the main concepts.

###### Parameters

```
{ "graphName": "test_bible_entities", "text": "Your text here",
  "modifyAnalyzedText": "extractEntitiesOnly" }
```

JSON

###### Response

```
{
  "mainTopicalClusters": ["Divine Temptation: [[god]] [[fruit]] [[tree]] [[the_serpent]] [[good_and_evil]] (0 | 100%)"],
  "mainConcepts": ["[[god]]", "[[fruit]]", "[[tree]]", "[[the_serpent]]", "[[good_and_evil]]"],
  "topRelations": ["1) [[god]] <-> [[the_serpent]]", "2) [[god]] <-> [[tree]]", "..."],
  "graphName": "test_bible_memory", "graphUrl": "https://infranodus.com/.../edit"
}
```

JSON

memory_get_relations

Retrieves memory from InfraNodus containing a specific entity, or all statements in a graph if entity is empty.

###### Parameters

`{ "memoryContextName": "test_bible_memory", "entity": "[[god]]" }`

JSON

###### Response

```
{
  "statements": ["[[God]] said, 'You shall not eat of the [[fruit]] of the [[tree]]...'"],
  "graphNames": ["test_bible_memory"],
  "graphUrls": ["https://infranodus.com/.../edit"]
}
```

JSON

## Text Comparison Tools

Compare multiple texts to find commonalities, differences, or build merged overviews. Useful for competitive analysis, content gap identification, and discourse overview from multiple sources.

difference_between_texts

Shows what's _missing_ in the first text/URL/graph that is _present_ in the others. The result shows the relations and clusters that are missing (not just keywords, since most texts use similar concepts but differ in relations). Useful for finding content gaps relative to existing discourse.

###### Parameters

```
{
  "contexts": [
    { "url": "https://infranodus.com" },
    { "text": "Network science meets cognitive variability" },
    { "graphName": "test_bible" }
  ], "includeStatements": true
}
```

JSON

###### Response

Returns `mainTopicalClusters`, `contentGaps`, `mainConcepts`, `topRelations`, and optionally `statements` that show only the content present in contexts 2+ but NOT in context 1.

overlap_between_texts

Finds common topics and relations that exist in _all_ provided texts, URLs, or graphs. Reveals common themes across specific content. If any context has no intersections with the rest, no results are shown.

###### Parameters

```
{
  "contexts": [
    { "graphName": "test_bible" },
    { "text": "Serpent is a woman's friend" },
    { "url": "https://www.biblegateway.com/passage/?search=Genesis%203&version=NIV" }
  ], "includeStatements": true
}
```

JSON

###### Response

Returns the `mainTopicalClusters`, `mainConcepts`, `topRelations`, and `statements` showing only the overlapping content found across all contexts.

merged_graph_from_texts

Generates a merged graph from several texts, URLs, and existing graphs. Provides information about main topics and gaps in a collection of documents. Useful for getting an overview of a discourse from various sources.

###### Parameters

```
{
  "contexts": [
    { "graphName": "test_bible" },
    { "text": "Serpent is a woman's friend" },
    { "url": "https://www.biblegateway.com/passage/?search=Genesis%203&version=NIV" }
  ]
}
```

JSON

###### Response

Returns `mainTopicalClusters`, `contentGaps`, `mainConcepts`, `topRelations` for the merged graph across all provided contexts.

## Google / SEO & LLMO Tools

Tools for optimizing content for search engines and LLMs. They access real search results and search intent data with statistical information about search volume and keyword popularity.

analyze_google_search_results

Generates a graph of the Google search results for a certain query. Useful for understanding which topics should be covered to gain topical authority. Set `includeSearchResults: true` to include URLs retrieved.

###### Parameters

`{ "queries": ["bible", "forbidden fruit"], "showExtendedGraphInfo": true }`

JSON

###### Response

Returns `statistics`, `graphSummary`, `contentGaps`, `mainTopicalClusters`, `mainConcepts`, `conceptualGateways`, `topRelations`, and `topInfluentialNodes` for the search results graph.

search_queries_vs_search_results

Finds search query clusters with high search volume that do not appear in Google search results — reveals content gaps in current informational supply. Use `includeSearchQueries: true` for actual queries with search volume.

###### Parameters

```
{ "queries": ["heart rate variability", "fitness trackers"],
  "showExtendedGraphInfo": true, "includeSearchQueries": true,
  "importLanguage": "EN", "importCountry": "US" }
```

JSON

###### Response

Returns `mainTopicalClusters` (e.g. "Fitness Accuracy", "HRV Monitoring"), `contentGaps` showing demand-supply mismatches, `conceptualGateways`, and `statements` with search volume data.

generate_seo_report

Full SEO report: extracts text and keywords, retrieves search results (topical authority), search intent (demand), then generates what people search for but don't find, and synthesizes content ideas and gap recommendations. Extract `header tags` or `link tags` for specific analysis. Execution may take 60-90 seconds.

###### Parameters

`{ "url": "https://infranodus.com", "contentToExtract": "header tags" }`

JSON

###### Response

```
{
  "inSearchResultsNotInText": {
    "mainTopics": ["1. Content Gaps: learn keyword analysis gap...", "..."],
    "conceptsToDevelop": ["learn", "seo", "keyword", "entity", "..."]
  },
  "inSearchQueriesNotInText": {
    "mainTopics": ["1. Insight Network: ai analysis knowledge graph...", "..."],
    "conceptsToDevelop": ["thinking", "infranodus", "analysis", "..."]
  },
  "inSearchQueriesNotInResults": {
    "mainTopics": ["1. PDF Tools: free tool seo...", "2. LLM Integration: graph llm knowledge python...", "..."],
    "conceptsToDevelop": ["tool", "free", "graph", "llm", "..."]
  },
  "topMissingQueries": [
    "content gap analysis ahrefs | 100 to 1000 searches/month",
    "knowledge graph llm | 100 to 1000 searches/month", "..." ]
}
```

JSON
