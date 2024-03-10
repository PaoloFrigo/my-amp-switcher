# typed: true
# frozen_string_literal: true

cask "myampswitcher" do
  version :latest
  description "MyAmpSwitcher is a Python app that allows you to control any device through MIDI messages."
  sha256 :no_check

  url "https://github.com/paolofrigo/my-amp-switcher/releases/latest/download/MyAmpSwitcher.dmg"
  name "MyAmpSwitcher"
  homepage "https://github.com/PaoloFrigo/my-amp-switcher"

  livecheck do
    url "https://api.github.com/repos/paolofrigo/my-amp-switcher/releases/latest"
    regex(/"tag_name":\s*"(.*?)".*?"name":\s*"(.*?)".*?"browser_download_url":\s*"(.*?)".*?/m)
    strategy :page_match do |page, regex|
      page.scan(regex).map { |match| match[0] }
    end
  end

  app "MyAmpSwitcher.app"
end
