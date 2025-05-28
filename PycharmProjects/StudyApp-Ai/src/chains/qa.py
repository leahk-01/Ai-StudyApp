from serpapi import GoogleSearch
from src.llm_config import llm

#  SerpAPI Config
SERPAPI_API_KEY = "4dca71e0572383eac36691e1f48b68b34722332538b17f91bcda303859226609"  # <--- Replace this!


def serpapi_web_search(query: str) -> str:
    """Use SerpAPI to search the web and return top results."""
    try:
        search = GoogleSearch({
            "q": query,
            "api_key": SERPAPI_API_KEY,
            "num": 5
        })
        results = search.get_dict()

        # Build a nice readable summary
        if "organic_results" in results:
            snippets = []
            for result in results["organic_results"][:5]:
                if "title" in result and "snippet" in result:
                    snippets.append(f"Title: {result['title']}\nSnippet: {result['snippet']}")
            if snippets:
                return "\n\n".join(snippets)

        # fallback if the format is unexpected
        return "No useful results found."

    except Exception as e:
        return f"Error with SerpAPI search: {str(e)}"


#Simple QA Chain

class ForceSearchQAChain:
    def __init__(self):
        pass

    @staticmethod
    def run(query):
        """Implementation that forcefully uses search results for every question."""
        try:
            # 1. Always search with the full query
            print(f"Searching for: {query}")
            primary_search_results = serpapi_web_search(query)

            # 2. Generate a better search query if needed
            if "No useful results found" in primary_search_results or len(primary_search_results) < 50:
                query_prompt = f"""
                You are an AI assistant creating an effective search query.
                Original question: {query}
                Create a short, focused search query (2-7 words) to find specific information.
                Only return the search query text with no extra text.
                """

                refined_query_response = llm.invoke(query_prompt)
                # Fix: Handle both string and object responses from LLM
                if hasattr(refined_query_response, 'content'):
                    refined_query = refined_query_response.content.strip()
                else:
                    refined_query = str(refined_query_response).strip()

                print(f"Refined search query: {refined_query}")

                # Search again with the refined query
                refined_search_results = serpapi_web_search(refined_query)

                # Combine results, with refined results first
                if "No useful results found" not in refined_search_results:
                    search_results = refined_search_results + "\n\n" + primary_search_results
                else:
                    search_results = primary_search_results
            else:
                search_results = primary_search_results

            print(f"Search results obtained, length: {len(search_results)}")

            # 3. Force the model to use these search results
            answer_prompt = f"""
            Answer this question using ONLY the search results provided below.

            Question: {query}

            Search Results:
            {search_results}

            Instructions:
            1. ONLY use information from the search results above.
            2. If the search results don't contain the answer, say "Based on the search results, I cannot find specific information about [topic]."
            4. Do NOT use any other knowledge not contained in the search results.
            5. Be concise but comprehensive.
            6. Start your answer directly with the relevant information.


            Your answer:
            """

            response = llm.invoke(answer_prompt)
            # Handle both string and object responses from LLM
            if hasattr(response, 'content'):
                answer = response.content.strip()
            else:
                answer = str(response).strip()

            # 4. Verify the response starts with the required text
            if not answer.startswith("Based on the search results"):
                # Force it to comply with a simpler prompt
                fallback_prompt = f"""
                Rewrite this answer to start with "Based on the search results, " and ONLY use information from these search results:

                Question: {query}
                Search Results: {search_results}

                Previous Answer: {answer}
                """
                fallback_response = llm.invoke(fallback_prompt)
                # Fix: Handle both string and object responses from LLM
                if hasattr(fallback_response, 'content'):
                    answer = fallback_response.content.strip()
                else:
                    answer = str(fallback_response).strip()

                # If it still doesn't comply, force it
                if not answer.startswith("Based on the search results"):
                    answer = "Based on the search results, " + answer

            return answer

        except Exception as e:
            error_message = f"Error in QA chain: {str(e)}"
            print(error_message)
            # Fallback to a direct search-based answer if any errors occur
            try:
                search_results = serpapi_web_search(query)
                return f"{search_results[:500]}..."
            except:
                return f"I encountered an error while searching for information about '{query}'. Please try rephrasing your question."


def get_qa_chain():
    return ForceSearchQAChain()
