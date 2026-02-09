import React, { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { adminAIAPI } from '@/lib/adminApi';
import { toast } from 'sonner';
import {
  Wand2,
  Sparkles,
  Tag,
  FileText,
  CheckCircle2,
  Loader2,
  Copy,
  ArrowRight,
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

interface AIBlogAssistantProps {
  open: boolean;
  onClose: () => void;
  onApply?: (data: any) => void;
  currentContent?: {
    title?: string;
    content?: string;
  };
}

export function AIBlogAssistant({
  open,
  onClose,
  onApply,
  currentContent,
}: AIBlogAssistantProps) {
  const [activeTab, setActiveTab] = useState('draft');
  const [loading, setLoading] = useState(false);

  // Draft Generation State
  const [draftTopic, setDraftTopic] = useState('');
  const [draftKeywords, setDraftKeywords] = useState('');
  const [draftTone, setDraftTone] = useState('professional');
  const [draftLength, setDraftLength] = useState('medium');
  const [generatedDraft, setGeneratedDraft] = useState<any>(null);

  // Content Improvement State
  const [improveContent, setImproveContent] = useState(currentContent?.content || '');
  const [improvementType, setImprovementType] = useState('general');
  const [improvedContent, setImprovedContent] = useState<any>(null);

  // Tag Suggestion State
  const [tagTitle, setTagTitle] = useState(currentContent?.title || '');
  const [tagContent, setTagContent] = useState(currentContent?.content || '');
  const [suggestedTags, setSuggestedTags] = useState<string[]>([]);

  // Title Suggestion State
  const [titleContent, setTitleContent] = useState(currentContent?.content || '');
  const [titleCount, setTitleCount] = useState(5);
  const [suggestedTitles, setSuggestedTitles] = useState<string[]>([]);

  // Summary Generation State
  const [summaryContent, setSummaryContent] = useState(currentContent?.content || '');
  const [summaryLength, setSummaryLength] = useState(150);
  const [generatedSummary, setGeneratedSummary] = useState('');

  // Quality Check State
  const [qualityTitle, setQualityTitle] = useState(currentContent?.title || '');
  const [qualityContent, setQualityContent] = useState(currentContent?.content || '');
  const [qualityReport, setQualityReport] = useState<any>(null);

  const handleGenerateDraft = async () => {
    if (!draftTopic.trim()) {
      toast.error('Please enter a topic');
      return;
    }

    setLoading(true);
    try {
      const keywords = draftKeywords
        .split(',')
        .map((k) => k.trim())
        .filter((k) => k);

      const response = await adminAIAPI.generateBlogDraft({
        topic: draftTopic,
        keywords: keywords.length > 0 ? keywords : undefined,
        tone: draftTone,
        length: draftLength,
      });

      setGeneratedDraft(response.data);
      toast.success('Blog draft generated successfully!');
    } catch (error: any) {
      toast.error(error.message || 'Failed to generate draft');
      console.error('Draft generation error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleImproveContent = async () => {
    if (!improveContent.trim()) {
      toast.error('Please enter content to improve');
      return;
    }

    setLoading(true);
    try {
      const response = await adminAIAPI.improveContent({
        content: improveContent,
        improvement_type: improvementType,
      });

      setImprovedContent(response.data);
      toast.success('Content improved successfully!');
    } catch (error: any) {
      toast.error(error.message || 'Failed to improve content');
      console.error('Content improvement error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSuggestTags = async () => {
    if (!tagTitle.trim() || !tagContent.trim()) {
      toast.error('Please enter both title and content');
      return;
    }

    setLoading(true);
    try {
      const response = await adminAIAPI.suggestTags({
        title: tagTitle,
        content: tagContent,
      });

      setSuggestedTags(response.data.tags);
      toast.success(`Generated ${response.data.tags.length} tag suggestions!`);
    } catch (error: any) {
      toast.error(error.message || 'Failed to suggest tags');
      console.error('Tag suggestion error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSuggestTitles = async () => {
    if (!titleContent.trim()) {
      toast.error('Please enter content');
      return;
    }

    setLoading(true);
    try {
      const response = await adminAIAPI.suggestTitles({
        content: titleContent,
        count: titleCount,
      });

      setSuggestedTitles(response.data.titles);
      toast.success(`Generated ${response.data.titles.length} title suggestions!`);
    } catch (error: any) {
      toast.error(error.message || 'Failed to suggest titles');
      console.error('Title suggestion error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateSummary = async () => {
    if (!summaryContent.trim()) {
      toast.error('Please enter content to summarize');
      return;
    }

    setLoading(true);
    try {
      const response = await adminAIAPI.generateSummary({
        content: summaryContent,
        max_length: summaryLength,
      });

      setGeneratedSummary(response.data.summary);
      toast.success('Summary generated successfully!');
    } catch (error: any) {
      toast.error(error.message || 'Failed to generate summary');
      console.error('Summary generation error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleQualityCheck = async () => {
    if (!qualityTitle.trim() || !qualityContent.trim()) {
      toast.error('Please enter both title and content');
      return;
    }

    setLoading(true);
    try {
      const response = await adminAIAPI.qualityCheck({
        title: qualityTitle,
        content: qualityContent,
      });

      setQualityReport(response.data);
      toast.success('Quality check completed!');
    } catch (error: any) {
      toast.error(error.message || 'Failed to check quality');
      console.error('Quality check error:', error);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast.success('Copied to clipboard!');
  };

  const applyResult = (data: any) => {
    if (onApply) {
      onApply(data);
    }
    toast.success('Applied to blog form!');
    onClose();
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Wand2 className="w-5 h-5 text-primary" />
            AI Blog Assistant
          </DialogTitle>
          <DialogDescription>
            Use AI to generate drafts, improve content, suggest tags and titles, and check
            quality
          </DialogDescription>
        </DialogHeader>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-6">
            <TabsTrigger value="draft">
              <Sparkles className="w-4 h-4 mr-1" />
              Draft
            </TabsTrigger>
            <TabsTrigger value="improve">
              <ArrowRight className="w-4 h-4 mr-1" />
              Improve
            </TabsTrigger>
            <TabsTrigger value="tags">
              <Tag className="w-4 h-4 mr-1" />
              Tags
            </TabsTrigger>
            <TabsTrigger value="titles">
              <FileText className="w-4 h-4 mr-1" />
              Titles
            </TabsTrigger>
            <TabsTrigger value="summary">Summary</TabsTrigger>
            <TabsTrigger value="quality">
              <CheckCircle2 className="w-4 h-4 mr-1" />
              Quality
            </TabsTrigger>
          </TabsList>

          {/* Draft Generation Tab */}
          <TabsContent value="draft" className="space-y-4">
            <div className="space-y-4">
              <div>
                <Label htmlFor="topic">Topic *</Label>
                <Input
                  id="topic"
                  placeholder="Enter blog topic (e.g., Managing Anxiety in Daily Life)"
                  value={draftTopic}
                  onChange={(e) => setDraftTopic(e.target.value)}
                />
              </div>

              <div>
                <Label htmlFor="keywords">Keywords (comma-separated)</Label>
                <Input
                  id="keywords"
                  placeholder="anxiety, mental health, coping strategies"
                  value={draftKeywords}
                  onChange={(e) => setDraftKeywords(e.target.value)}
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="tone">Tone</Label>
                  <Select value={draftTone} onValueChange={setDraftTone}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="professional">Professional</SelectItem>
                      <SelectItem value="casual">Casual</SelectItem>
                      <SelectItem value="friendly">Friendly</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label htmlFor="length">Length</Label>
                  <Select value={draftLength} onValueChange={setDraftLength}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="short">Short (~300 words)</SelectItem>
                      <SelectItem value="medium">Medium (~600 words)</SelectItem>
                      <SelectItem value="long">Long (~1000 words)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <Button onClick={handleGenerateDraft} disabled={loading} className="w-full">
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Generating...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4 mr-2" />
                    Generate Draft
                  </>
                )}
              </Button>

              {generatedDraft && (
                <Card className="mt-4">
                  <CardHeader>
                    <CardTitle className="flex items-center justify-between">
                      Generated Draft
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => applyResult(generatedDraft)}
                      >
                        Apply to Form
                      </Button>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <Label>Title</Label>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => copyToClipboard(generatedDraft.title)}
                        >
                          <Copy className="w-4 h-4" />
                        </Button>
                      </div>
                      <p className="font-semibold">{generatedDraft.title}</p>
                    </div>

                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <Label>Content</Label>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => copyToClipboard(generatedDraft.content)}
                        >
                          <Copy className="w-4 h-4" />
                        </Button>
                      </div>
                      <div className="bg-gray-50 p-4 rounded-md max-h-64 overflow-y-auto whitespace-pre-wrap">
                        {generatedDraft.content}
                      </div>
                    </div>

                    {generatedDraft.tags && generatedDraft.tags.length > 0 && (
                      <div>
                        <Label className="mb-2 block">Suggested Tags</Label>
                        <div className="flex flex-wrap gap-2">
                          {generatedDraft.tags.map((tag: string, index: number) => (
                            <Badge key={index} variant="secondary">
                              {tag}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>
              )}
            </div>
          </TabsContent>

          {/* Content Improvement Tab */}
          <TabsContent value="improve" className="space-y-4">
            <div className="space-y-4">
              <div>
                <Label htmlFor="improve-content">Content to Improve *</Label>
                <Textarea
                  id="improve-content"
                  placeholder="Paste your blog content here..."
                  value={improveContent}
                  onChange={(e) => setImproveContent(e.target.value)}
                  rows={8}
                />
              </div>

              <div>
                <Label htmlFor="improvement-type">Improvement Type</Label>
                <Select value={improvementType} onValueChange={setImprovementType}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="general">General Improvement</SelectItem>
                    <SelectItem value="clarity">Improve Clarity</SelectItem>
                    <SelectItem value="engagement">Boost Engagement</SelectItem>
                    <SelectItem value="tone">Adjust Tone</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <Button onClick={handleImproveContent} disabled={loading} className="w-full">
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Improving...
                  </>
                ) : (
                  <>
                    <ArrowRight className="w-4 h-4 mr-2" />
                    Improve Content
                  </>
                )}
              </Button>

              {improvedContent && (
                <Card className="mt-4">
                  <CardHeader>
                    <CardTitle className="flex items-center justify-between">
                      Improved Content
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => copyToClipboard(improvedContent.improved_content)}
                      >
                        <Copy className="w-4 h-4 mr-2" />
                        Copy
                      </Button>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="bg-gray-50 p-4 rounded-md max-h-64 overflow-y-auto whitespace-pre-wrap">
                      {improvedContent.improved_content}
                    </div>

                    {improvedContent.suggestions && improvedContent.suggestions.length > 0 && (
                      <div>
                        <Label className="mb-2 block">Suggestions</Label>
                        <ul className="list-disc pl-5 space-y-1 text-sm text-gray-600">
                          {improvedContent.suggestions.map((suggestion: string, index: number) => (
                            <li key={index}>{suggestion}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </CardContent>
                </Card>
              )}
            </div>
          </TabsContent>

          {/* Tag Suggestion Tab */}
          <TabsContent value="tags" className="space-y-4">
            <div className="space-y-4">
              <div>
                <Label htmlFor="tag-title">Blog Title *</Label>
                <Input
                  id="tag-title"
                  placeholder="Enter blog title..."
                  value={tagTitle}
                  onChange={(e) => setTagTitle(e.target.value)}
                />
              </div>

              <div>
                <Label htmlFor="tag-content">Blog Content *</Label>
                <Textarea
                  id="tag-content"
                  placeholder="Paste blog content..."
                  value={tagContent}
                  onChange={(e) => setTagContent(e.target.value)}
                  rows={6}
                />
              </div>

              <Button onClick={handleSuggestTags} disabled={loading} className="w-full">
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Generating Tags...
                  </>
                ) : (
                  <>
                    <Tag className="w-4 h-4 mr-2" />
                    Suggest Tags
                  </>
                )}
              </Button>

              {suggestedTags.length > 0 && (
                <Card className="mt-4">
                  <CardHeader>
                    <CardTitle>Suggested Tags</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex flex-wrap gap-2">
                      {suggestedTags.map((tag, index) => (
                        <Badge
                          key={index}
                          variant="secondary"
                          className="cursor-pointer"
                          onClick={() => copyToClipboard(tag)}
                        >
                          {tag}
                        </Badge>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          </TabsContent>

          {/* Title Suggestion Tab */}
          <TabsContent value="titles" className="space-y-4">
            <div className="space-y-4">
              <div>
                <Label htmlFor="title-content">Blog Content *</Label>
                <Textarea
                  id="title-content"
                  placeholder="Paste your blog content..."
                  value={titleContent}
                  onChange={(e) => setTitleContent(e.target.value)}
                  rows={8}
                />
              </div>

              <div>
                <Label htmlFor="title-count">Number of Suggestions</Label>
                <Input
                  id="title-count"
                  type="number"
                  min="1"
                  max="10"
                  value={titleCount}
                  onChange={(e) => setTitleCount(parseInt(e.target.value) || 5)}
                />
              </div>

              <Button onClick={handleSuggestTitles} disabled={loading} className="w-full">
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Generating Titles...
                  </>
                ) : (
                  <>
                    <FileText className="w-4 h-4 mr-2" />
                    Suggest Titles
                  </>
                )}
              </Button>

              {suggestedTitles.length > 0 && (
                <Card className="mt-4">
                  <CardHeader>
                    <CardTitle>Suggested Titles</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      {suggestedTitles.map((title, index) => (
                        <div
                          key={index}
                          className="p-3 bg-gray-50 rounded-md flex items-center justify-between hover:bg-gray-100 transition-colors"
                        >
                          <span className="flex-1">{title}</span>
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => copyToClipboard(title)}
                          >
                            <Copy className="w-4 h-4" />
                          </Button>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          </TabsContent>

          {/* Summary Generation Tab */}
          <TabsContent value="summary" className="space-y-4">
            <div className="space-y-4">
              <div>
                <Label htmlFor="summary-content">Content to Summarize *</Label>
                <Textarea
                  id="summary-content"
                  placeholder="Paste your blog content..."
                  value={summaryContent}
                  onChange={(e) => setSummaryContent(e.target.value)}
                  rows={8}
                />
              </div>

              <div>
                <Label htmlFor="summary-length">Maximum Length (words)</Label>
                <Input
                  id="summary-length"
                  type="number"
                  min="50"
                  max="300"
                  value={summaryLength}
                  onChange={(e) => setSummaryLength(parseInt(e.target.value) || 150)}
                />
              </div>

              <Button onClick={handleGenerateSummary} disabled={loading} className="w-full">
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Generating Summary...
                  </>
                ) : (
                  <>
                    <FileText className="w-4 h-4 mr-2" />
                    Generate Summary
                  </>
                )}
              </Button>

              {generatedSummary && (
                <Card className="mt-4">
                  <CardHeader>
                    <CardTitle className="flex items-center justify-between">
                      Generated Summary
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => copyToClipboard(generatedSummary)}
                      >
                        <Copy className="w-4 h-4 mr-2" />
                        Copy
                      </Button>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-gray-700">{generatedSummary}</p>
                  </CardContent>
                </Card>
              )}
            </div>
          </TabsContent>

          {/* Quality Check Tab */}
          <TabsContent value="quality" className="space-y-4">
            <div className="space-y-4">
              <div>
                <Label htmlFor="quality-title">Blog Title *</Label>
                <Input
                  id="quality-title"
                  placeholder="Enter blog title..."
                  value={qualityTitle}
                  onChange={(e) => setQualityTitle(e.target.value)}
                />
              </div>

              <div>
                <Label htmlFor="quality-content">Blog Content *</Label>
                <Textarea
                  id="quality-content"
                  placeholder="Paste blog content..."
                  value={qualityContent}
                  onChange={(e) => setQualityContent(e.target.value)}
                  rows={8}
                />
              </div>

              <Button onClick={handleQualityCheck} disabled={loading} className="w-full">
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <CheckCircle2 className="w-4 h-4 mr-2" />
                    Check Quality
                  </>
                )}
              </Button>

              {qualityReport && (
                <Card className="mt-4">
                  <CardHeader>
                    <CardTitle>Quality Report</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <Label>Overall Score</Label>
                        <p className="text-3xl font-bold text-primary">
                          {qualityReport.overall_score}/10
                        </p>
                      </div>
                      <div>
                        <Label>Readability</Label>
                        <p className="text-2xl font-semibold">{qualityReport.readability_level}</p>
                      </div>
                    </div>

                    {qualityReport.tone_assessment && (
                      <div>
                        <Label>Tone Assessment</Label>
                        <p className="text-gray-700">{qualityReport.tone_assessment}</p>
                      </div>
                    )}

                    {qualityReport.word_count && (
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <Label>Word Count</Label>
                          <p className="font-medium">{qualityReport.word_count}</p>
                        </div>
                        <div>
                          <Label>Estimated Read Time</Label>
                          <p className="font-medium">{qualityReport.estimated_read_time}</p>
                        </div>
                      </div>
                    )}

                    {qualityReport.strengths && qualityReport.strengths.length > 0 && (
                      <div>
                        <Label className="mb-2 block text-green-700">Strengths</Label>
                        <ul className="list-disc pl-5 space-y-1 text-sm text-gray-700">
                          {qualityReport.strengths.map((strength: string, index: number) => (
                            <li key={index}>{strength}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {qualityReport.improvements && qualityReport.improvements.length > 0 && (
                      <div>
                        <Label className="mb-2 block text-orange-700">Suggested Improvements</Label>
                        <ul className="list-disc pl-5 space-y-1 text-sm text-gray-700">
                          {qualityReport.improvements.map((improvement: string, index: number) => (
                            <li key={index}>{improvement}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </CardContent>
                </Card>
              )}
            </div>
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
}
