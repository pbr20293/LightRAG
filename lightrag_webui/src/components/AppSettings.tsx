import { useState, useCallback, useEffect } from 'react'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/Popover'
import Button from '@/components/ui/Button'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/Select'
import Checkbox from '@/components/ui/Checkbox'
import Badge from '@/components/ui/Badge'
import { useSettingsStore } from '@/stores/settings'
import { PaletteIcon, BeakerIcon } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { cn } from '@/lib/utils'
import { getPromptMode, setPromptMode } from '@/api/lightrag'
import { toast } from 'sonner'

interface AppSettingsProps {
  className?: string
}

export default function AppSettings({ className }: AppSettingsProps) {
  const [opened, setOpened] = useState<boolean>(false)
  const [promptModeLoading, setPromptModeLoading] = useState<boolean>(false)
  const { t } = useTranslation()

  const language = useSettingsStore.use.language()
  const setLanguage = useSettingsStore.use.setLanguage()

  const theme = useSettingsStore.use.theme()
  const setTheme = useSettingsStore.use.setTheme()

  const useEngineeringPrompts = useSettingsStore.use.useEngineeringPrompts()
  const setUseEngineeringPrompts = useSettingsStore.use.setUseEngineeringPrompts()
  const promptModeEntityTypes = useSettingsStore.use.promptModeEntityTypes()
  const setPromptModeEntityTypes = useSettingsStore.use.setPromptModeEntityTypes()

  // Load prompt mode on component mount
  useEffect(() => {
    const loadPromptMode = async () => {
      try {
        const response = await getPromptMode()
        setUseEngineeringPrompts(response.use_engineering_prompts)
        setPromptModeEntityTypes(response.entity_types)
      } catch (error) {
        console.error('Failed to load prompt mode:', error)
      }
    }

    if (opened) {
      loadPromptMode()
    }
  }, [opened, setUseEngineeringPrompts, setPromptModeEntityTypes])

  const handleLanguageChange = useCallback((value: string) => {
    setLanguage(value as 'en' | 'zh' | 'fr' | 'ar' | 'zh_TW')
  }, [setLanguage])

  const handleThemeChange = useCallback((value: string) => {
    setTheme(value as 'light' | 'dark' | 'system')
  }, [setTheme])

  const handlePromptModeChange = useCallback(async (checked: boolean) => {
    setPromptModeLoading(true)
    try {
      const response = await setPromptMode({ use_engineering_prompts: checked })
      setUseEngineeringPrompts(response.use_engineering_prompts)
      setPromptModeEntityTypes(response.entity_types)
      
      toast.success(response.message, {
        description: checked 
          ? "Switched to Engineering Standards mode" 
          : "Switched to General Knowledge Graph mode"
      })
    } catch (error) {
      console.error('Failed to set prompt mode:', error)
      toast.error("Failed to update prompt mode", {
        description: "Please try again or restart the server"
      })
    } finally {
      setPromptModeLoading(false)
    }
  }, [setUseEngineeringPrompts, setPromptModeEntityTypes])

  return (
    <Popover open={opened} onOpenChange={setOpened}>
      <PopoverTrigger asChild>
        <Button variant="ghost" size="icon" className={cn('h-9 w-9', className)}>
          <PaletteIcon className="h-5 w-5" />
        </Button>
      </PopoverTrigger>
      <PopoverContent side="bottom" align="end" className="w-56">
        <div className="flex flex-col gap-4">
          <div className="flex flex-col gap-2">
            <label className="text-sm font-medium">{t('settings.language')}</label>
            <Select value={language} onValueChange={handleLanguageChange}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="en">English</SelectItem>
                <SelectItem value="zh">中文</SelectItem>
                <SelectItem value="fr">Français</SelectItem>
                <SelectItem value="ar">العربية</SelectItem>
                <SelectItem value="zh_TW">繁體中文</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="flex flex-col gap-2">
            <label className="text-sm font-medium">{t('settings.theme')}</label>
            <Select value={theme} onValueChange={handleThemeChange}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="light">{t('settings.light')}</SelectItem>
                <SelectItem value="dark">{t('settings.dark')}</SelectItem>
                <SelectItem value="system">{t('settings.system')}</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="flex flex-col gap-3 border-t border-border pt-3">
            <div className="flex items-center space-x-3">
              <BeakerIcon className="h-4 w-4 text-muted-foreground" />
              <div className="flex flex-col flex-1">
                <label className="text-sm font-medium">Prompt Mode</label>
                <p className="text-xs text-muted-foreground">
                  {useEngineeringPrompts 
                    ? "Engineering standards extraction" 
                    : "General knowledge graphs"
                  }
                </p>
              </div>
              <Checkbox 
                checked={useEngineeringPrompts}
                onCheckedChange={handlePromptModeChange}
                disabled={promptModeLoading}
              />
            </div>
            
            {promptModeEntityTypes.length > 0 && (
              <div className="flex flex-col gap-2">
                <p className="text-xs text-muted-foreground">Entity Types:</p>
                <div className="flex flex-wrap gap-1 max-h-20 overflow-y-auto">
                  {promptModeEntityTypes.slice(0, 8).map((type) => (
                    <Badge key={type} variant="secondary" className="text-xs">
                      {type}
                    </Badge>
                  ))}
                  {promptModeEntityTypes.length > 8 && (
                    <Badge variant="outline" className="text-xs">
                      +{promptModeEntityTypes.length - 8} more
                    </Badge>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </PopoverContent>
    </Popover>
  )
}
