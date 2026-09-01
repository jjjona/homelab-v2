FROM debian:12-slim

ARG NODE_VERSION=22.23.2
ARG TMUX_VERSION=3.5a

RUN apt-get update && apt-get install -y --no-install-recommends \
      bash build-essential bison ca-certificates curl git libevent-dev \
      libncurses-dev openssh-client pkg-config unzip xz-utils \
    && curl -fsSL "https://nodejs.org/dist/v${NODE_VERSION}/node-v${NODE_VERSION}-linux-x64.tar.xz" \
      | tar -xJ -C /usr/local --strip-components=1 \
    && curl -fsSL "https://github.com/oven-sh/bun/releases/download/bun-v1.3.14/bun-linux-x64.zip" -o /tmp/bun.zip \
    && unzip -q /tmp/bun.zip -d /tmp \
    && install -m 0755 /tmp/bun-linux-x64/bun /usr/local/bin/bun \
    && curl -fsSL "https://github.com/tmux/tmux/releases/download/${TMUX_VERSION}/tmux-${TMUX_VERSION}.tar.gz" -o /tmp/tmux.tar.gz \
    && tar -xzf /tmp/tmux.tar.gz -C /tmp \
    && cd "/tmp/tmux-${TMUX_VERSION}" \
    && ./configure --prefix=/usr/local \
    && make -j2 \
    && make install \
    && useradd --create-home --uid 1000 --shell /bin/bash workspace \
    && su - workspace -c 'npm install -g --ignore-scripts --prefix /home/workspace/.local @earendil-works/pi-coding-agent@0.84.4' \
    && ln -s /home/workspace/.local/bin/pi /usr/local/bin/pi \
    && rm -rf /var/lib/apt/lists/* /tmp/*

COPY --chown=workspace:workspace project-starter /opt/project-starter
COPY --chown=workspace:workspace pi-working-discipline /opt/pi-working-discipline
COPY --chown=workspace:workspace start-workspace.sh /usr/local/bin/start-workspace

RUN cd /opt/project-starter \
    && bun install --frozen-lockfile \
    && bun run build \
    && chmod 0755 /usr/local/bin/start-workspace \
    && su - workspace -c 'PI_CODING_AGENT_DIR=/home/workspace/.pi/agent /opt/pi-working-discipline/install.sh'

USER workspace
WORKDIR /workspace
ENV HOME=/home/workspace
EXPOSE 4484
ENTRYPOINT ["/usr/local/bin/start-workspace"]
