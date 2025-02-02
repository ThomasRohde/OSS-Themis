from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import hashlib
import json
from itertools import permutations

# Import your existing project modules.
from bcm.models import LayoutModel
from bcm.settings import Settings

# -----------------------------------------------------------------------------
# New constants for visual layout improvements (tweak these as needed)
# -----------------------------------------------------------------------------
HORIZONTAL_GAP_FACTOR = 0.05     # Relative gap: 5% of average child width.
VERTICAL_GAP_FACTOR = 0.05       # Relative gap: 5% of average child height.
UNIFORM_CELLS = True             # Use uniform cells based on the largest child.
USE_COMPOSITE_METRIC = False     # Use a composite metric (aspect ratio + area penalty).
AREA_PENALTY_FACTOR = 0.001      # Penalty factor for total area if composite metric is used.
SORT_CHILDREN = True             # Sort children (by area) for larger sets.
# -----------------------------------------------------------------------------


@dataclass
class NodeSize:
    width: float
    height: float


@dataclass
class GridLayout:
    rows: int
    cols: int
    width: float
    height: float
    deviation: float
    positions: List[Dict[str, float]]


@dataclass
class LayoutResult:
    """
    A container to return both the best layout
    and the best child ordering (permutation) that produced it.
    """
    layout: GridLayout
    permutation: List[int]  # Indices of child_sizes in the best order


@dataclass(frozen=True)
class CacheKey:
    """Represents a unique key for caching layout calculations"""
    node_id: int
    settings_hash: str

    def __hash__(self):
        return hash((self.node_id, self.settings_hash))


class LayoutCache:
    def __init__(self):
        self._size_cache: Dict[CacheKey, NodeSize] = {}
        self._layout_cache: Dict[Tuple[Tuple[int, ...], str], LayoutResult] = {}

    def get_node_size(self, key: CacheKey) -> Optional[NodeSize]:
        return self._size_cache.get(key)

    def set_node_size(self, key: CacheKey, size: NodeSize):
        self._size_cache[key] = size

    def get_layout(self, child_ids: Tuple[int, ...], settings_hash: str) -> Optional[LayoutResult]:
        return self._layout_cache.get((child_ids, settings_hash))

    def set_layout(self, child_ids: Tuple[int, ...], settings_hash: str, result: LayoutResult):
        self._layout_cache[(child_ids, settings_hash)] = result


def hash_settings(settings: Settings) -> str:
    """Create a stable hash of settings that affect layout (old settings only)."""
    relevant_settings = {
        'box_min_width': settings.get('box_min_width'),
        'box_min_height': settings.get('box_min_height'),
        'horizontal_gap': settings.get('horizontal_gap'),
        'vertical_gap': settings.get('vertical_gap'),
        'padding': settings.get('padding'),
        'top_padding': settings.get('top_padding'),
        'target_aspect_ratio': settings.get('target_aspect_ratio'),
    }
    settings_str = json.dumps(relevant_settings, sort_keys=True)
    return hashlib.sha256(settings_str.encode()).hexdigest()


def calculate_node_size(
    node: LayoutModel,
    settings: Settings,
    cache: LayoutCache,
    settings_hash: str
) -> NodeSize:
    """Calculate the minimum bounding size needed for a node and its children, with caching."""
    cache_key = CacheKey(node.id, settings_hash)
    cached_size = cache.get_node_size(cache_key)
    if cached_size is not None:
        return cached_size

    if not node.children:
        size = NodeSize(settings.get("box_min_width"), settings.get("box_min_height"))
    else:
        # Recursively calculate sizes for all children.
        child_sizes = [
            calculate_node_size(child, settings, cache, settings_hash)
            for child in node.children
        ]
        child_ids = tuple(child.id for child in node.children)
        layout_result = cache.get_layout(child_ids, settings_hash)
        if layout_result is None:
            layout_result = find_best_layout(child_sizes, len(child_sizes), settings)
            cache.set_layout(child_ids, settings_hash, layout_result)
        size = NodeSize(layout_result.layout.width, layout_result.layout.height)

    cache.set_node_size(cache_key, size)
    return size


def compute_grid_layout(
    perm_sizes: List[NodeSize],
    rows: int,
    cols: int,
    settings: Settings
) -> GridLayout:
    """
    Compute the grid layout (dimensions and child positions) for a given number
    of rows and columns. Supports both uniform (default) and adaptive cell sizing.
    """
    child_count = len(perm_sizes)

    # Use constant-based dynamic gap computation.
    avg_child_width = sum(size.width for size in perm_sizes) / child_count
    horizontal_gap = HORIZONTAL_GAP_FACTOR * avg_child_width

    avg_child_height = sum(size.height for size in perm_sizes) / child_count
    vertical_gap = VERTICAL_GAP_FACTOR * avg_child_height

    padding = settings.get("padding", 20.0)
    top_padding = settings.get("top_padding", padding)
    target_aspect_ratio = settings.get("target_aspect_ratio", 1.6)

    # Use the constant for uniform cell layout.
    uniform = UNIFORM_CELLS

    if uniform:
        # Use uniform cell dimensions based on the largest child.
        uniform_width = max(size.width for size in perm_sizes)
        uniform_height = max(size.height for size in perm_sizes)

        grid_width = cols * uniform_width + (cols - 1) * horizontal_gap
        grid_height = rows * uniform_height + (rows - 1) * vertical_gap
        total_width = grid_width + 2 * padding
        total_height = grid_height + top_padding + padding

        aspect_ratio = total_width / total_height
        deviation = (aspect_ratio - target_aspect_ratio) ** 2
        if USE_COMPOSITE_METRIC:
            deviation += AREA_PENALTY_FACTOR * (total_width * total_height)

        positions = []
        for r in range(rows):
            for c in range(cols):
                idx = r * cols + c
                if idx < child_count:
                    child = perm_sizes[idx]
                    cell_x = padding + c * (uniform_width + horizontal_gap)
                    cell_y = top_padding + r * (uniform_height + vertical_gap)
                    # Center the child within its uniform cell.
                    x_offset = cell_x + (uniform_width - child.width) / 2
                    y_offset = cell_y + (uniform_height - child.height) / 2
                    pos = {
                        "x": round(x_offset),
                        "y": round(y_offset),
                        "width": round(child.width),
                        "height": round(child.height)
                    }
                    positions.append(pos)

        max_child_bottom = max((pos["y"] + pos["height"]) for pos in positions) if positions else 0
        actual_height = max_child_bottom + padding

        return GridLayout(
            rows=rows,
            cols=cols,
            width=round(total_width),
            height=round(actual_height),
            deviation=deviation,
            positions=positions
        )
    else:
        # Adaptive layout: compute per-row heights and per-column widths.
        row_heights = [0.0] * rows
        col_widths = [0.0] * cols

        for i, size in enumerate(perm_sizes):
            r = i // cols
            c = i % cols
            row_heights[r] = max(row_heights[r], size.height)
            col_widths[c] = max(col_widths[c], size.width)

        grid_width = sum(col_widths) + (cols - 1) * horizontal_gap
        grid_height = sum(row_heights) + (rows - 1) * vertical_gap
        total_width = grid_width + 2 * padding
        total_height = grid_height + top_padding + padding

        aspect_ratio = total_width / total_height
        deviation = (aspect_ratio - target_aspect_ratio) ** 2
        if USE_COMPOSITE_METRIC:
            deviation += AREA_PENALTY_FACTOR * (total_width * total_height)

        positions = []
        y_offset = top_padding
        for r in range(rows):
            x_offset = padding
            for c in range(cols):
                idx = r * cols + c
                if idx < child_count:
                    child = perm_sizes[idx]
                    extra_width = col_widths[c] - child.width
                    extra_height = row_heights[r] - child.height
                    pos = {
                        "x": round(x_offset + extra_width / 2),
                        "y": round(y_offset + extra_height / 2),
                        "width": round(child.width),
                        "height": round(child.height)
                    }
                    positions.append(pos)
                    x_offset += col_widths[c] + horizontal_gap
            y_offset += row_heights[r] + vertical_gap

        max_child_bottom = max((pos["y"] + pos["height"]) for pos in positions) if positions else 0
        actual_height = max_child_bottom + padding

        return GridLayout(
            rows=rows,
            cols=cols,
            width=round(total_width),
            height=round(actual_height),
            deviation=deviation,
            positions=positions
        )


def _try_layout_for_permutation(
    perm_sizes: List[NodeSize],
    permutation: List[int],
    child_count: int,
    settings: Settings,
) -> GridLayout:
    """
    For the given permutation of child sizes (perm_sizes), try all row/column combinations
    and return the best GridLayout found according to the composite metric.
    """
    local_best_layout = GridLayout(
        rows=1,
        cols=child_count,
        width=float("inf"),
        height=float("inf"),
        deviation=float("inf"),
        positions=[],
    )

    for rows_tentative in range(1, child_count + 1):
        for cols_float in [child_count / rows_tentative, (child_count + rows_tentative - 1) // rows_tentative]:
            cols = int(round(cols_float))
            if cols <= 0:
                continue

            # Compute the number of rows needed.
            rows = (child_count + cols - 1) // cols

            candidate_layout = compute_grid_layout(perm_sizes, rows, cols, settings)

            if (candidate_layout.deviation < local_best_layout.deviation) or (
                abs(candidate_layout.deviation - local_best_layout.deviation) < 1e-9 and
                (candidate_layout.width * candidate_layout.height < local_best_layout.width * local_best_layout.height)
            ):
                local_best_layout = candidate_layout

    return local_best_layout


def find_best_layout(
    child_sizes: List[NodeSize],
    child_count: int,
    settings: Settings
) -> LayoutResult:
    """
    Find the best grid layout for the given child sizes.
    - For small sets (child_count <= MAX_PERMUTATION_CHILDREN), all permutations are tested.
    - For larger sets, a heuristic ordering (by area, if enabled) is used.
    Returns both the best layout and the permutation that produced it.
    """
    MAX_PERMUTATION_CHILDREN = 8
    best_layout = GridLayout(
        rows=1,
        cols=child_count,
        width=float("inf"),
        height=float("inf"),
        deviation=float("inf"),
        positions=[],
    )
    best_perm = list(range(child_count))

    def check_permutation(
        perm: List[int],
        best_layout: GridLayout,
        best_perm: List[int]
    ) -> Tuple[GridLayout, List[int]]:
        perm_sizes = [child_sizes[i] for i in perm]
        candidate_layout = _try_layout_for_permutation(perm_sizes, perm, child_count, settings)
        if (candidate_layout.deviation < best_layout.deviation) or (
            abs(candidate_layout.deviation - best_layout.deviation) < 1e-9 and
            (candidate_layout.width * candidate_layout.height < best_layout.width * best_layout.height)
        ):
            return candidate_layout, list(perm)
        else:
            return best_layout, best_perm

    do_permutations = child_count <= MAX_PERMUTATION_CHILDREN
    if do_permutations:
        for perm in permutations(range(child_count)):
            best_layout, best_perm = check_permutation(list(perm), best_layout, best_perm)
    else:
        # Use heuristic ordering: sort children by area (largest first) if enabled.
        identity_perm = list(range(child_count))
        if SORT_CHILDREN:
            identity_perm = sorted(identity_perm, key=lambda i: child_sizes[i].width * child_sizes[i].height, reverse=True)
        best_layout, best_perm = check_permutation(identity_perm, best_layout, best_perm)

    return LayoutResult(layout=best_layout, permutation=best_perm)


def layout_tree(
    node: LayoutModel,
    settings: Settings,
    cache: LayoutCache,
    settings_hash: str,
    x: float = 0.0,
    y: float = 0.0
) -> LayoutModel:
    """
    Recursively layout the tree starting from the given node.
    Uses caching and applies the best grid layout to the children.
    """
    if not node.children:
        node.width = settings.get("box_min_width")
        node.height = settings.get("box_min_height")
        node.x = x
        node.y = y
        return node

    child_sizes = [
        calculate_node_size(child, settings, cache, settings_hash)
        for child in node.children
    ]

    child_ids = tuple(child.id for child in node.children)
    layout_result = cache.get_layout(child_ids, settings_hash)
    if layout_result is None:
        layout_result = find_best_layout(child_sizes, len(child_sizes), settings)
        cache.set_layout(child_ids, settings_hash, layout_result)

    # Reorder children according to the best permutation.
    node.children = [node.children[i] for i in layout_result.permutation]
    child_sizes = [child_sizes[i] for i in layout_result.permutation]

    node.x = x
    node.y = y
    node.width = layout_result.layout.width
    node.height = layout_result.layout.height

    # Place each child using the computed positions.
    for child, pos in zip(node.children, layout_result.layout.positions):
        layout_tree(child, settings, cache, settings_hash, x + pos["x"], y + pos["y"])
        child.width = pos["width"]
        child.height = pos["height"]

    return node


def process_layout(model: LayoutModel, settings: Settings) -> LayoutModel:
    """
    ALGORITHM DESCRIPTION:

    This layout algorithm computes a visually pleasing grid arrangement for a tree of nodes, where each node may have
    multiple children. The overall goal is to determine a grid configuration (i.e., number of rows and columns) and
    child ordering that best matches a target aspect ratio and minimizes wasted space, while also allowing for uniform
    or adaptive cell sizing.

    Key Steps:

    1. Recursive Layout Calculation with Caching:
    - For each node in the tree, the algorithm computes the minimum bounding size required.
    - If the node has no children, it uses a default size (from the settings).
    - For nodes with children, it recursively calculates the sizes of each child.
    - Results (both node sizes and grid layouts) are cached using a key based on the node's ID and a hash of
        the settings. This caching prevents redundant calculations when the same subtree or settings are encountered again.

    2. Grid Layout Optimization:
    - When a node has children, the algorithm computes an optimal grid layout for placing these children.
    - The process involves:
        a. Trying Different Row/Column Configurations:
            - The algorithm iterates over possible numbers of rows (from 1 up to the number of children).
            - For each row count, it calculates the corresponding number of columns needed to accommodate all children.
        b. Cell Sizing (Uniform vs. Adaptive):
            - If UNIFORM_CELLS is enabled, all grid cells are set to the same size, based on the largest child.
            Each child is then centered within its cell.
            - Otherwise, an adaptive approach is used where each row’s height is determined by the tallest child in that row,
            and each column’s width by the widest child in that column.
        c. Gaps and Padding:
            - Horizontal and vertical gaps between cells are computed dynamically using constant gap factors relative to
            the average child dimensions.
            - Additional padding is applied around the grid (with options for top and side padding).
        d. Goodness Metric (Layout Score):
            - The “goodness” of a layout is measured by how close the grid’s aspect ratio (total width divided by total height)
            is to a target value.
            - The deviation is calculated as the squared difference between the computed and target aspect ratios.
            - Optionally, a composite metric can be used by adding an area penalty (proportional to the total grid area) to the deviation.
            This encourages more compact layouts.

    3. Permutation and Heuristic Ordering:
    - For nodes with a small number of children (up to MAX_PERMUTATION_CHILDREN), the algorithm tests every possible permutation
        of child ordering. The permutation that results in the best (lowest) deviation score is selected.
    - For larger sets of children, testing all permutations is computationally prohibitive. Instead, a heuristic ordering is used,
        such as sorting children by their area (largest first), to approximate an optimal layout without exhaustive search.

    4. Final Layout Assignment:
    - Once the optimal grid layout and child ordering are determined, the algorithm updates the node:
        - The node’s dimensions are set to enclose the entire grid.
        - Each child's position and size are assigned based on the computed grid positions, with coordinates rounded for pixel alignment.
    - The layout process is then applied recursively to each child node.

    Overall, the algorithm strikes a balance between aesthetic design (achieving a target aspect ratio, centering within cells,
    and consistent spacing) and computational efficiency (via caching and heuristic ordering). The use of constants for key parameters
    (such as gap factors, uniform cell preference, and penalty factors) makes it easy to tweak the visual appearance without altering
    the core logic.
    """

    cache = LayoutCache()
    settings_hash = hash_settings(settings)
    return layout_tree(model, settings, cache, settings_hash)
