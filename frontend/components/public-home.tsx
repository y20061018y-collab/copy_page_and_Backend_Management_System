"use client";

import React, { useEffect, useMemo, useState, type CSSProperties } from "react";
import styles from "./public-home.module.css";

export type Service = {
  id: number;
  name: string;
  description: string;
  cover_image?: string;
  items: ServiceItem[];
};

export type ServiceItem = {
  id: number;
  name: string;
  price: string;
  description: string;
};

export type Game = {
  id: number;
  name: string;
  slug: string;
  tag: string;
  description: string;
  cover_image: string;
  accent_color: string;
  accent_color_2: string;
  services: Service[];
};

export type Settings = {
  site_name: string;
  site_subtitle: string;
  studio_image: string | null;
  contact_wechat: string | null;
  contact_qq: string | null;
  contact_phone: string | null;
  contact_description: string | null;
};

const STUDIO_IMAGE = "/images/studio.jpg";

export function featuredServices<T>(services: T[]): T[] {
  return services.slice(0, 5);
}

export function modalRows<T>(services: T[]): T[] {
  return services;
}

export function gameDetails({ tag, description }: Pick<Game, "tag" | "description">): string[] {
  return [tag, description].filter(Boolean);
}

export default function PublicHome({ games, settings }: { games: Game[]; settings: Settings }) {
  const firstGame = games[0] ?? null;
  const [selectedGameSlug, setSelectedGameSlug] = useState(firstGame?.slug ?? "");
  const [selectedService, setSelectedService] = useState<Service | null>(null);
  const [showContact, setShowContact] = useState(false);
  const [copied, setCopied] = useState<string | null>(null);

  useEffect(() => {
    setSelectedGameSlug((current) => {
      if (games.some((game) => game.slug === current)) return current;
      return games[0]?.slug ?? "";
    });
  }, [games]);

  useEffect(() => {
    const close = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setSelectedService(null);
        setShowContact(false);
      }
    };

    window.addEventListener("keydown", close);
    return () => window.removeEventListener("keydown", close);
  }, []);

  const selectedGame = useMemo(
    () => games.find((game) => game.slug === selectedGameSlug) ?? firstGame,
    [firstGame, games, selectedGameSlug],
  );

  const services = selectedGame?.services ?? [];
  const visibleServices = featuredServices(services);
  const studioImage = settings.studio_image?.trim() || STUDIO_IMAGE;
  const wechat = settings.contact_wechat?.trim() || null;
  const qq = settings.contact_qq?.trim() || null;
  const phone = settings.contact_phone?.trim() || null;

  const copy = async (kind: string, value: string) => {
    try {
      await navigator.clipboard.writeText(value.trim());
      setCopied(kind);
      window.setTimeout(() => setCopied(null), 1600);
    } catch {
      setCopied(null);
    }
  };

  const openService = (service: Service) => {
    setSelectedService(service);
    setShowContact(false);
  };

  const openContact = () => {
    setSelectedService(null);
    setShowContact(true);
  };

  if (!selectedGame) {
    return (
      <main className={styles.page}>
        <Header settings={settings} studioImage={studioImage} onContact={openContact} />
        <section className={styles.emptyState}>
          <p>ELEVEN ESPORTS STUDIO</p>
          <h1>暂无可展示游戏</h1>
          <span>请在后台添加并启用游戏服务。</span>
        </section>
      </main>
    );
  }

  return (
    <main className={styles.page}>
      <Header settings={settings} studioImage={studioImage} onContact={openContact} />

      <section className={styles.hero}>
        <div>
          <p className={styles.eyebrow}>ELEVEN ESPORTS STUDIO</p>
          <h1>
            把游戏交给<span>专业的人</span>
          </h1>
          <p className={styles.heroDescription}>
            稳定 · 高效 · 值得信赖
            <br />
            专注每一次成长体验
          </p>
        </div>

        <div className={styles.heroEmblem} aria-hidden="true">
          <div className={styles.emblemFrame}>
            <img src={studioImage} alt="" />
          </div>
        </div>
      </section>

      <section className={styles.workspace} id="games">
        <aside>
          <div className={styles.sectionIntro}>
            <h2>选择你的游戏</h2>
            <p>每一份服务，都为更好的游戏体验而生</p>
          </div>

          <div className={styles.gameList}>
            {games.map((game) => {
              const isSelected = game.slug === selectedGame.slug;

              return (
                <button
                  className={`${styles.gameButton} ${isSelected ? styles.activeGame : ""}`}
                  key={game.slug}
                  onClick={() => setSelectedGameSlug(game.slug)}
                  type="button"
                  style={{ "--game-accent": game.accent_color } as CSSProperties}
                >
                  <img className={styles.gameIcon} src={game.cover_image} alt={game.name} />
                  <span>
                    <strong>{game.name}</strong>
                    <small>{gameDetails(game).join(" · ")}</small>
                  </span>
                  {isSelected && <i aria-hidden="true">→</i>}
                </button>
              );
            })}
          </div>
        </aside>

        <section className={styles.demands} aria-live="polite">
          <div className={styles.demandTitle}>
            <div>
              <p>需求</p>
              <h2>{selectedGame.name} · 服务需求</h2>
            </div>
            <span>{visibleServices.length} 项需求</span>
          </div>

          <div className={styles.demandList}>
            {visibleServices.length > 0 ? (
              visibleServices.map((service, index) => {
                return (
                  <button
                    className={styles.demandCard}
                    key={service.id}
                    onClick={() => openService(service)}
                    type="button"
                  >
                    <b className={index === 1 ? styles.cyanBadge : ""}>{String(index + 1).padStart(2, "0")}</b>
                    <span>
                      <strong>{service.name}</strong>
                      {service.description?.trim() && <small>{service.description}</small>}
                    </span>
                  </button>
                );
              })
            ) : (
              <article className={styles.emptyDemand}>该游戏暂未配置服务，请在后台添加需求内容。</article>
            )}
          </div>
        </section>
      </section>

      <footer className={styles.footer}>
        <div className={styles.brand}>
          <span className={styles.brandImageWrap}>
            <img src={studioImage} alt="工作室图标" />
          </span>
          <strong>{settings.site_name}</strong>
          <span>{settings.site_subtitle}</span>
        </div>
        <small>© 2026 11号电竞工作室</small>
      </footer>

      {selectedService && (
        <ServiceModal
          game={selectedGame}
          selectedService={selectedService}
          onClose={() => setSelectedService(null)}
        />
      )}

      {showContact && (
        <ContactModal
          settings={settings}
          wechat={wechat}
          qq={qq}
          phone={phone}
          copied={copied}
          onClose={() => setShowContact(false)}
          onCopy={copy}
        />
      )}
    </main>
  );
}

function Header({
  settings,
  studioImage,
  onContact,
}: {
  settings: Settings;
  studioImage: string;
  onContact: () => void;
}) {
  return (
    <header className={styles.nav}>
      <div className={styles.brand}>
        <span className={styles.brandImageWrap}>
          <img src={studioImage} alt="工作室图标" />
        </span>
        <strong>{settings.site_name}</strong>
        <span>{settings.site_subtitle}</span>
      </div>

      <button className={styles.consultButton} onClick={onContact} type="button">
        立即咨询
      </button>
    </header>
  );
}

export function ServiceModal({
  game,
  selectedService,
  onClose,
}: {
  game: Game;
  selectedService: Service;
  onClose: () => void;
}) {
  const orderedItems = modalRows(selectedService.items);
  const serviceCover = selectedService.cover_image || game.cover_image;

  return (
    <div className={styles.modalBackdrop} onClick={onClose}>
      <section
        className={styles.serviceModal}
        role="dialog"
        aria-modal="true"
        aria-label={`${game.name}服务详情`}
        onClick={(event) => event.stopPropagation()}
      >
        <button className={styles.modalClose} onClick={onClose} type="button" aria-label="关闭服务详情">
          ×
        </button>

        <figure className={styles.modalCover}>
          <img src={serviceCover} alt={`${selectedService.name}服务封面`} />
          <figcaption>
            <span>{game.name} · {selectedService.name}</span>
          </figcaption>
        </figure>

        <div className={styles.priceList} aria-label={`${selectedService.name}子项目报价明细`}>
          {orderedItems.length > 0 ? orderedItems.map((item) => {
            return (
              <article
                className={styles.priceRow}
                key={item.id}
              >
                <div>
                  <h3>{item.name}</h3>
                  {item.description?.trim() && <p>{item.description}</p>}
                </div>
                {item.price?.trim() && <strong>{item.price}</strong>}
              </article>
            );
          }) : <p className={styles.emptyItems}>该大项目暂未配置子项目，请在后台添加。</p>}
        </div>
      </section>
    </div>
  );
}

function ContactModal({
  settings,
  wechat,
  qq,
  phone,
  copied,
  onClose,
  onCopy,
}: {
  settings: Settings;
  wechat: string | null;
  qq: string | null;
  phone: string | null;
  copied: string | null;
  onClose: () => void;
  onCopy: (kind: string, value: string) => void;
}) {
  const hasContact = Boolean(wechat || qq || phone);

  return (
    <div className={styles.modalBackdrop} onClick={onClose}>
      <section
        className={styles.contactModal}
        role="dialog"
        aria-modal="true"
        aria-label="立即咨询"
        onClick={(event) => event.stopPropagation()}
      >
        <button className={styles.modalClose} onClick={onClose} type="button" aria-label="关闭联系方式">
          ×
        </button>
        <p className={styles.eyebrow}>CONTACT US</p>
        <h2>立即咨询</h2>
        <p>{settings.contact_description ?? "欢迎联系我们咨询服务详情"}</p>

        {wechat && (
          <button className={styles.contactRow} onClick={() => onCopy("wechat", wechat)} type="button">
            <span>微信</span>
            <strong>{wechat}</strong>
            <small>{copied === "wechat" ? "已复制" : "复制"}</small>
          </button>
        )}

        {qq && (
          <button className={styles.contactRow} onClick={() => onCopy("qq", qq)} type="button">
            <span>QQ</span>
            <strong>{qq}</strong>
            <small>{copied === "qq" ? "已复制" : "复制"}</small>
          </button>
        )}

        {phone && (
          <div className={styles.contactRow}>
            <span>电话</span>
            <strong>{phone}</strong>
            <button onClick={() => onCopy("phone", phone)} type="button">
              {copied === "phone" ? "已复制" : "复制"}
            </button>
            <a href={`tel:${phone}`}>拨打</a>
          </div>
        )}

        {!hasContact && <span className={styles.noContact}>联系方式尚未配置，请联系管理员。</span>}
      </section>
    </div>
  );
}
