#-*- coding:utf8 -*-
from collections import defaultdict

class Optimizer(object):

  @classmethod
  def optimize(cls, ops_info, topo_order, output_nodes, method='None'):
    """
    [(op_name, op_info, ref_counts, to_eval), ...]
    """
    opt_function = _OPTIMIZE_METHODS.get(method, None)
    if opt_function is None:
      raise ValueError("unknown optimization method: {}".format(method))
    return opt_function(ops_info, topo_order, output_nodes)

def findAndReplace(tensorList, target, new_val):
  for i, item in enumerate(tensorList):
    if item == target:
      tensorList[i] = new_val
  return tensorList

def _no_optimize(ops_info, topo_order, output_nodes):
  optimized_order = []
  for op_name in topo_order[::-1]:
    op_info = ops_info[op_name]

    # pass to remove dropout
    # might mess with ref_count
    if op_info.op_type == "dropout":
      dropout_input_node = op_info.input_tensor[0]
      dropout_output_node = op_info.output_tensor[0]
      ops_info[dropout_input_node].output_tensor = findAndReplace(ops_info[dropout_input_node].output_tensor, dropout_input_node, dropout_output_node)
      ops_info[dropout_output_node].input_tensor = findAndReplace(ops_info[dropout_output_node].input_tensor, dropout_output_node, dropout_input_node)
      print("dropout with name ", op_name, " has been removed")
      continue

    ref_cnts = [0 for _ in op_info.output_tensor]
    optimized_order.append((op_name, op_info, ref_cnts, False))
  return optimized_order


def _refcnt_optimize(ops_info, topo_order, output_nodes):
  """Optimization using only reference count
  """
  optimized_order = []

  refcnt_table = _tensor_ref_count(ops_info)
  for op_name in topo_order[::-1]:
    op_info = ops_info[op_name]
    if op_name in output_nodes or op_info.op_type in ["Const", "Placeholder"]:
      to_eval = False
    else:
      to_eval = True
    ref_counts = [refcnt_table[out_tname] for out_tname, _, _ in op_info.output_tensor]
    optimized_order.append((op_name, op_info, ref_counts, to_eval))
  return optimized_order


def _tensor_ref_count(ops_info):
  tensor_ref_count = defaultdict(lambda: 0)
  for op_info in ops_info.values():
    for tname, _, _ in op_info.input_tensor:
      tensor_ref_count[tname] += 1
  return tensor_ref_count


_OPTIMIZE_METHODS = {
  'None': _no_optimize,
  'refcnt': _refcnt_optimize
}
