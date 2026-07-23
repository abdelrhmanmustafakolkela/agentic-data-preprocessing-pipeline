from langgraph.graph import StateGraph, END
from app.state import PipelineState
from app.agents.understand_data import understand_data
from app.agents.plan_preprocessing import plan_preprocessing
from app.agents.execute_preprocessing import execute_preprocessing
from app.agents.plan_charts import plan_charts
from app.agents.generate_charts import generate_charts


def create_pipeline_graph() -> StateGraph:
    workflow = StateGraph(PipelineState)
    workflow.add_node("understand_data", understand_data)
    workflow.add_node("plan_preprocessing", plan_preprocessing)
    workflow.add_node("execute_preprocessing", execute_preprocessing)
    workflow.add_node("plan_charts", plan_charts)
    workflow.add_node("generate_charts", generate_charts)
    workflow.set_entry_point("understand_data")
    workflow.add_edge("understand_data", "plan_preprocessing")
    workflow.add_edge("plan_preprocessing", "execute_preprocessing")
    workflow.add_edge("execute_preprocessing", "plan_charts")
    workflow.add_edge("plan_charts", "generate_charts")
    workflow.add_edge("generate_charts", END)
    app = workflow.compile()
    return app


_pipeline_graph = None


def get_pipeline_graph() -> StateGraph:
    global _pipeline_graph
    if _pipeline_graph is None:
        _pipeline_graph = create_pipeline_graph()
    return _pipeline_graph
