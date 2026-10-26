# from types import SimpleNamespace
# from unittest.mock import MagicMock
# from agent import ContextAwareAgent, ContextMode

# def _choice(*, content=None, tool_calls=None, reasoning=None):
#     msg = SimpleNamespace(
#         content=content, tool_calls=tool_calls, reasoning_content=reasoning,
#         model_dump=lambda: {
#             "role": "assistant", "content": content,
#             "reasoning_content": reasoning,
#             "tool_calls": [
#                 {"id": tc.id, "type": "function",
#                  "function": {"name": tc.function.name,
#                               "arguments": tc.function.arguments}}
#                 for tc in (tool_calls or [])
#             ],
#         },
#     )
#     return SimpleNamespace(message=msg)

# def _response(choice, resp_id):
#     # 顶层的 model_dump 让 api_turns 里带上 response.id —— 契约要靠它
#     return SimpleNamespace(
#         id=resp_id, choices=[choice],
#         model_dump=lambda: {"id": resp_id,
#                             "choices": [choice.message.model_dump()]},
#     )

# call = SimpleNamespace(id="call-1",
#     function=SimpleNamespace(name="calculate",
#                              arguments='{"expression": "2 + 2"}'))
# turn1 = _response(_choice(tool_calls=[call], reasoning="I should add."), "resp-1")
# #turn2 = _response(_choice(content="FINAL ANSWER: 4", reasoning="Done."), "resp-2")
# turn2 = _response(_choice(content="", reasoning="Done."), "resp-2")

# agent = ContextAwareAgent("test-key", ContextMode.FULL, verbose=False)
# agent.client = MagicMock()
# agent.client.chat.completions.create = MagicMock(side_effect=[turn1, turn2])

# result = agent.execute_task("compute 2+2", max_iterations=5)

# print(result["completed"], result["final_answer"])
# print(agent.client.chat.completions.create.call_count)
# for t in agent.trajectory.api_turns:
#     print(t["iteration"], [m["role"] for m in t["request"]["messages"]])


# from run_experiment_1_1 import evaluate_context_contract
# def turn(messages, *, tools=True, reasoning="reason", resp_id="resp-1"):
#     req = {"messages": messages}
#     if tools:
#         req.update({"tools": [{"type": "function"}], "tool_choice": "auto"})
#     return {"request": req,
#             "response": {"id": resp_id,
#                          "choices": [{"message": {"reasoning_content": reasoning}}]}}

# SYSTEM  = {"role": "system", "content": "system"}
# USER    = {"role": "user",   "content": "task"}
# ASSIST  = {"role": "assistant", "reasoning_content": "reason",
#            "tool_calls": [{"id": "call"}]}
# TOOL    = {"role": "tool", "content": '{"result": 4}'}
# HIDDEN  = {"role": "tool", "content": "[Tool result hidden due to context mode]"}
# STRIPPED = {k: v for k, v in ASSIST.items() if k != "reasoning_content"}
# cases = {
#     "full":         [turn([SYSTEM, USER]),turn([SYSTEM,USER,ASSIST,TOOL])],
#     # "no_history":      [turn([SYSTEM, USER]), turn([SYSTEM, USER])],
#     "no_history":      [turn([SYSTEM, USER]),turn([SYSTEM,USER,ASSIST,TOOL])],
#     "no_reasoning":    [turn([SYSTEM, USER]), turn([SYSTEM, USER, STRIPPED, TOOL])],
#     "no_tool_results": [turn([SYSTEM, USER]), turn([SYSTEM, USER, ASSIST, HIDDEN])],
#     "no_tool_calls":   [turn([SYSTEM, USER], tools=False)],
# }
# for mode, turns in cases.items():
#     r = evaluate_context_contract(mode, turns)
#     print(mode, r["passed"], r["required_checks"])

from agent import AgentTrajectory, ContextMode
from run_experiment_1_1 import summarize_arm, canonical_answer_correct

def arm(final_answer, mode=ContextMode.NO_TOOL_CALLS, iterations=1):
    done = final_answer is not None
    return {"trajectory": AgentTrajectory(context_mode=mode),
            "final_answer": final_answer, "completed": done,
            "success": done, "iterations": iterations,
            "provider": "test", "model": "test-model"}

refusal = "I cannot compute the exchange rates without tools."
a = summarize_arm(ContextMode.NO_TOOL_CALLS, arm(refusal), elapsed=0.1)
print(a["completed"], a["success"], a["task_success"], a["behavior"])
# True True False {...}

good = "Annual total: $9,602,895.73; quarterly average: $2,400,723.93"
b = summarize_arm(ContextMode.NO_TOOL_RESULTS,
                  arm(good, mode=ContextMode.NO_TOOL_RESULTS), elapsed=0.1)
print(b["task_success"])   # True —— 即使这个臂被消融过,答对了就是答对了