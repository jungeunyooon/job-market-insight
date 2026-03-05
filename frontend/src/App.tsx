import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Layout } from '@/components/layout/Layout'
import { SkillRanking } from '@/pages/SkillRanking'
import { CompanyProfile } from '@/pages/CompanyProfile'
import { PositionCompare } from '@/pages/PositionCompare'
import { GapAnalysis } from '@/pages/GapAnalysis'
import { JobSearch } from '@/pages/JobSearch'
import { BuzzVsHiring } from '@/pages/BuzzVsHiring'
import { BlogTrend } from '@/pages/BlogTrend'
import { SkillMindmap } from '@/pages/SkillMindmap'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<SkillRanking />} />
          <Route path="company" element={<CompanyProfile />} />
          <Route path="compare" element={<PositionCompare />} />
          <Route path="gap" element={<GapAnalysis />} />
          <Route path="search" element={<JobSearch />} />
          <Route path="buzz" element={<BuzzVsHiring />} />
          <Route path="blog-trend" element={<BlogTrend />} />
          <Route path="mindmap" element={<SkillMindmap />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
