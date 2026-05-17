import { useState } from "react";

interface GuideSection {
  id: string;
  title: string;
  icon: string;
  content: string;
}

const guideSections: GuideSection[] = [
  {
    id: "welcome",
    title: "Welcome to Meshwork",
    icon: "🌐",
    content: `Meshwork is a community-owned mesh networking device that provides free internet access to everyone within 300 feet.

**Key Features:**
- Zero monthly fees - no carrier, no subscription
- Zero technical knowledge required - works out of the box
- Zero setup - plug it in and it auto-configures
- Zero ongoing cost - powered by ambient energy (RF, solar, thermal)

Your Meshwork device harvests ambient energy, connects to free TV White Space spectrum for broadband backhaul, and self-organizes with neighboring devices to blanket your neighborhood in free, community-owned internet.`
  },
  {
    id: "getting-started",
    title: "Getting Started",
    icon: "🚀",
    content: `**First Steps:**

1. **Place your device** - Put your Meshwork device on a windowsill or location with good exposure to ambient energy sources and TV White Space signals.

2. **Power on** - Connect your device to power. It will automatically begin harvesting energy and connecting to the mesh network.

3. **Wait for connection** - Your device will scan for neighbors and connect to the best available gateway. This may take a few minutes.

4. **Check your status** - Use the Dashboard tab to monitor your device's health, connection status, and contribution to the network.

5. **Connect your devices** - Once connected, you can use the free internet access for all your devices within range.`
  },
  {
    id: "dashboard",
    title: "Dashboard Tab",
    icon: "📊",
    content: `The Dashboard tab shows your device's overall health and performance.

**Status Card displays:**
- **Node Health** - Overall device status (online/offline)
- **Neighbors** - Number of nearby Meshwork devices
- **Generosity** - How much bandwidth you're sharing with the network
- **Power Mode** - Current power state based on harvested energy

**Metrics Chart shows:**
- 30-day history of your bandwidth contribution
- Gateway activity timeline (purple = active as gateway)
- Track your impact on the community network

**Power Modes:**
- Full Operation: >500 mW harvested - everything on
- Reduced: 100-500 mW - 50% power, lower beacon rate
- Low Power: 10-100 mW - beacon only, no routing
- Sleep: <10 mW - deep sleep mode`
  },
  {
    id: "network",
    title: "Network Tab",
    icon: "🔗",
    content: `The Network tab visualizes your mesh network connections.

**Location Map:**
- Shows your device's geographic position
- Displays neighbor devices in your area
- Visual representation of network coverage

**Constellation Map:**
- Animated visualization of mesh topology
- Shows connections between devices
- Signal strength indicators (green = strong, blue = medium, white = weak)
- Live data packet animation on connections

**Neighbor Map:**
- List of all nearby Meshwork devices
- Each neighbor shows:
  - Node ID (unique identifier)
  - Signal strength (RSSI in dBm)
  - Latency (response time)
  - Generosity score (bandwidth sharing)
- Gateway nodes are highlighted with a badge

**Understanding Gateways:**
Gateways are nodes that connect the mesh to the broader internet. The AI automatically routes traffic through the best gateway based on latency, bandwidth, and reliability.`
  },
  {
    id: "controls",
    title: "Controls Tab",
    icon: "⚙️",
    content: `The Controls tab lets you configure your device's behavior.

**Gateway Mode:**
- Toggle your device to act as a gateway for the network
- When enabled, your device shares its internet connection with neighbors
- Requires authentication token
- Only enable if you have reliable internet connection to share
- Green button = gateway active, Red button = gateway inactive

**Bandwidth Cap:**
- Set maximum bandwidth you're willing to share
- Slider from 0-100 Mbps
- Helps manage your network contribution
- Protects your own internet experience
- Changes apply immediately

**Authentication:**
- Control tab requires authentication token for safety
- Token is generated on first server boot
- Enter token in the input field to unlock controls
- Token is saved in your browser for convenience

**Best Practices:**
- Enable gateway mode only if you have stable, fast internet
- Set bandwidth cap to 50-70% of your total bandwidth
- Monitor your contribution on the Dashboard
- Disable gateway mode if you experience performance issues`
  },
  {
    id: "concepts",
    title: "Key Concepts",
    icon: "💡",
    content: `**Mesh Networking:**
A decentralized network where each device connects to nearby devices, creating a web of connections. If one path fails, traffic automatically routes through another.

**TV White Space (TVWS):**
Unused frequencies between TV channels that can be used for wireless internet. Provides long-range, reliable backhaul connections without traditional ISPs.

**Ambient Energy Harvesting:**
Your device collects energy from the environment:
- RF energy from radio signals
- Solar energy (even indoors)
- Thermal energy from temperature differences

**Gateway Nodes:**
Devices that connect the mesh network to the broader internet. They share their connection with neighbors, expanding network coverage.

**Generosity Score:**
A metric (0-100%) showing how much bandwidth you're contributing to the network. Higher scores mean you're helping more people get free internet.

**AI-Powered Routing:**
The system uses AI to automatically select the best gateway based on:
- Latency (40% weight)
- Bandwidth availability (35% weight)
- Generosity history (15% weight)
- Signal strength (10% weight)`
  },
  {
    id: "troubleshooting",
    title: "Troubleshooting",
    icon: "🔧",
    content: `**Device Not Connecting:**
- Ensure device has power and is placed near a window
- Check that TV White Space signals are available in your area
- Wait 5-10 minutes for initial scanning and connection
- Try moving device to a different location

**Slow Connection:**
- Check your power mode in Dashboard
- Low power modes reduce performance
- Move device to location with better energy harvesting
- Reduce distance from gateway nodes

**No Neighbors Found:**
- You may be the first in your area
- Encourage neighbors to join the network
- More neighbors = stronger, faster network
- Check device placement for better signal

**Gateway Mode Issues:**
- Verify your internet connection is stable
- Check bandwidth cap isn't too low
- Ensure authentication token is correct
- Disable and re-enable gateway mode

**Device in Sleep Mode:**
- Normal when harvested energy is very low
- Device will wake automatically when energy improves
- Move to location with better ambient energy
- Check energy harvesting components

**For persistent issues:**
- Check server logs for error messages
- Verify firmware is up to date
- Contact community support
- Report bugs on GitHub`
  },
  {
    id: "community",
    title: "Community & Support",
    icon: "🤝",
    content: `**Join the Community:**
Meshwork is an open-source project built by volunteers and community members like you.

**Ways to Contribute:**
- Run a gateway node to expand coverage
- Share bandwidth with neighbors
- Report bugs and suggest features
- Contribute code on GitHub
- Help new users get started
- Spread the word about free community internet

**Get Help:**
- Check this guide for common questions
- Visit the GitHub repository for documentation
- Join community discussions
- Ask questions in forums
- Contact support for technical issues

**The Vision:**
The internet should be infrastructure owned by communities, like roads and water. Meshwork makes this reality possible - one device at a time.

**One device. One windowsill. Free internet for your whole neighborhood. Forever.**

Thank you for being part of the Meshwork community! 🌐`
  }
];

export default function UserGuide() {
  const [activeSection, setActiveSection] = useState(guideSections[0].id);

  const activeGuide = guideSections.find(s => s.id === activeSection);

  return (
    <div className="user-guide">
      <div className="card">
        <div className="card-header">
          <h2>User Guide</h2>
          <span className="version">v1.0</span>
        </div>

        <div className="guide-layout">
          <nav className="guide-nav">
            {guideSections.map(section => (
              <button
                key={section.id}
                className={`guide-nav-item ${activeSection === section.id ? "active" : ""}`}
                onClick={() => setActiveSection(section.id)}
              >
                <span className="guide-nav-icon">{section.icon}</span>
                <span className="guide-nav-text">{section.title}</span>
              </button>
            ))}
          </nav>

          <div className="guide-content">
            <div className="guide-section">
              <h3>
                <span className="guide-section-icon">{activeGuide?.icon}</span>
                {activeGuide?.title}
              </h3>
              <div className="guide-text">
                {activeGuide?.content.split('\n').map((line, i) => {
                  if (line.startsWith('**') && line.endsWith('**')) {
                    return <strong key={i}>{line.slice(2, -2)}</strong>;
                  }
                  if (line.startsWith('- ')) {
                    return <li key={i}>{line.slice(2)}</li>;
                  }
                  if (line.match(/^\d+\./)) {
                    return <li key={i}>{line}</li>;
                  }
                  if (line.trim() === '') {
                    return <br key={i} />;
                  }
                  return <p key={i}>{line}</p>;
                })}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
