cask "myampswitcher" do
    name "MyAmpSwitcher"
    description "MyAmpSwitcher is a Python application that allows you to control your amplifier, amp-cab-switcher or any device through MIDI messages. You can switch between different profiles, each containing customizable buttons that send MIDI Program Change and Control Change messages. This software is released under the MIT license."
    version :latest
    homepage "https://github.com/PaoloFrigo/my-amp-switcher"

    livecheck do
      url "https://api.github.com/repos/paolofrigo/my-amp-switcher/releases/latest"
      regex(%r{"tag_name":\s*"(.*?)".*?"name":\s*"(.*?)".*?"browser_download_url":\s*"(.*?)".*?}m)
      strategy :page_match do |page, regex|
        page.scan(regex).map { |match| match[0] }
      end
    end

    url "https://github.com/paolofrigo/my-amp-switcher/releases/latest/download/MyAmpSwitcher.dmg"
    sha256 :no_check

    app "MyAmpSwitcher.app"


    caveats do
    end
  end
