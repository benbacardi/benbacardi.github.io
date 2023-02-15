title: Lessons Learnt from an Outage
category: Networking

I caused an outage last week. 

Not intentionally, and not a large outage by any stretch of the imagination. But it had various knock-on consequences that led to a lengthy application recovery time, long after full network connectivity was restored.

We were replacing one of the two core MPLS routers at one of the three primary sites in our network. Upgrading the hardware to a newer model required costing the existing node out, powering it off, physically replacing it with the new hardware, and bringing the node back online.

(For those of you interested in the details, we were upgrading a Juniper MX480 to an MX10003 - all logical connectivity was staying the same, but some links were being upgraded from 10Gbps to either 40 or 100).

In preparation for the upgrade, I had taken the running config from the existing node, adapted what was necessary for the newer hardware (mainly interface name changes, etc) and preloaded it onto the new node waiting in the lab. So far so good.

Unfortunately, the running config at the time I took it from the live node, was exactly that - the _live_ node. At that moment, it wasn't in its costed-out state, meaning that the minute we started repatching links into the new hardware, they were coming back live.

These core node provide connectivity between our three primary sites, and their three data centres. As the links came up live, the new node started drawing traffic from the local data centre fabric before it had any connectivity to the other sites (or even the other node in the same site). This meant that for a period of around four minutes, between one sixth and one half of all egress traffic from the local data centre was being blackholed, and dropped.

This caused connectivity issues between our ceph clusters, which then struggled to make sense of the situation, and filled up the only remaining link between this site and the others with traffic. (I don't know the full details of why it did this, or what that traffic was - I'm a network engineer, and not responsible for the rest of the infrastructure. But remember I said we were upgrading from 10 to 100Gbps on some links? This is partly why). This then exacerbated the connectivity problems (for other applications in addition to ceph), pinning the links at line rate long after the we had costed out the new node as originally intended, leading to the long recovery time for the application layer.

So what did I learn from this outage? That's the most important question when something like this happens - particularly if it was your fault. This is what I learnt.

### Don't become complacent

We had done this exact procedure for the other node in this site just days before, and all had gone smoothly (I had remembered to cost out the new node as I was preparing its config, instead of running with the live config from the existing node). Even if you've done an identical change before, _always_ triple check what you're doing if it has the potential to cause an impact on other parts of the business. Ideally, ask a colleague if they can spot anything you may have forgotten.

### Unconditional summarisation isn't always a good thing

Even though the links weren't costed out, if all the core did was pass on routes learnt from the other sites, then the new node wouldn't have started drawing traffic until it was able to route it.§

Instead, our core currently advertises three aggregate routes to its clients - the three private [RFC1918](https://tools.ietf.org/html/rfc1918) ranges. These aggregates are active if just a single contributing route is present in the routing table. In our case, the core node's loopback is a perfectly valid contributing route to the 10.0.0.0/8 aggregate, causing it to be advertised even if every other link on the box was down, drawing (and dropping) traffic.

Under normal circumstances, we'd obviously expect the core nodes to have full reachability to the rest of the core, and this wouldn't be an issue. However, certain failure scenarios can cause a node to become isolated (not just configuration mistakes like this one!) and blackhole traffic. Advertising more specific routes actually learnt from other peers, or some conditions imposed on the generation of the aggregate routes, would help limit this.

### Be selective about the order links are repatched

Core-facing links first! The outage was caused by the fact that the links to the data centre fabric were connected before the core-facing links. If they had been done the other way around, and core connectivity as part of the MPLS domain was confirmed before connecting any client-facing links, the issue would have been avoided.

Core-facing links are more important than client-facing - most clients will have redundancy via other nodes, and even if they don't, until your core node has reachability to the rest of the core, it's useless to its clients anyway.

### Don't neglect CoS

While not directly related to the outage itself, ceph filling the links with non-essential traffic (compared to, say, production web or database traffic) led to outages on other applications that could no longer communicate. Some quality of service markings and traffic shaping or policing would have a gone a long way to mitigating the impact, by restricting non-business-critical traffic to a subset of the link. Less important (but still useful) on the upgraded 100Gbps connections; but our single 10Gbps like couldn't cope.

