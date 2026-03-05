declare module 'react-force-graph-2d' {
  import { Component } from 'react'

  interface NodeObject {
    id: string
    [key: string]: unknown
  }

  interface LinkObject {
    source: string | NodeObject
    target: string | NodeObject
    [key: string]: unknown
  }

  interface GraphData {
    nodes: NodeObject[]
    links: LinkObject[]
  }

  interface ForceGraph2DProps {
    graphData: GraphData
    width?: number
    height?: number
    nodeLabel?: string | ((node: NodeObject) => string)
    nodeColor?: string | ((node: NodeObject) => string)
    nodeVal?: string | number | ((node: NodeObject) => number)
    nodeRelSize?: number
    linkColor?: string | ((link: LinkObject) => string)
    linkWidth?: number | ((link: LinkObject) => number)
    onNodeClick?: (node: NodeObject, event: MouseEvent) => void
    onNodeHover?: (node: NodeObject | null, prevNode: NodeObject | null) => void
    cooldownTicks?: number
    d3AlphaDecay?: number
    d3VelocityDecay?: number
    backgroundColor?: string
    nodeCanvasObject?: (node: NodeObject, ctx: CanvasRenderingContext2D, globalScale: number) => void
    [key: string]: unknown
  }

  export default class ForceGraph2D extends Component<ForceGraph2DProps> {}
}
