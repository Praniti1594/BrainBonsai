(function () {
  'use strict';

  function hash(str) {
    let h = 0;
    for (let i = 0; i < str.length; i++) {
      h = ((h << 5) - h) + str.charCodeAt(i) | 0;
    }
    return Math.abs(h).toString(16);
  }

  function makeAddress(seed) {
    const h = hash(seed).padStart(8, '0').slice(-8);
    return '0x' + h.toUpperCase().slice(0, 4) + '...' + h.toUpperCase().slice(-4);
  }

  function makeTxHash(seed) {
    const h = hash(seed).padStart(8, '0').slice(-8);
    return '0x' + h.toUpperCase() + 'af31';
  }

  const addresses = {
    main: makeAddress('brainbonsai-main'),
    friend: makeAddress('brainbonsai-friend')
  };

  const state = {
    mainBalance: 100,
    mainCollectibles: 0,
    transferYouBalance: 100,
    transferFriendBalance: 50,
    treeStage: 0,
    gasLevel: 1,
    transactions: [],
    completedSteps: { receive: false, send: false, send10: false, fee: false, approve: false },
    pendingTransfer: null
  };

  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => root.querySelectorAll(sel);

  function getGasFee() {
    const fees = [0.5, 1, 2];
    return fees[state.gasLevel] || 1;
  }

  function getConfirmDelay() {
    const delays = [2000, 1200, 500];
    return delays[state.gasLevel] || 1200;
  }

  function updateMainWallet(direction) {
    const el = $('#main-balance');
    if (el) {
      el.textContent = state.mainBalance;
      el.classList.remove('balance-up', 'balance-down');
      el.offsetHeight;
      if (direction === 'up') el.classList.add('balance-up');
      else if (direction === 'down') el.classList.add('balance-down');
    }
    const coll = $('#main-collectibles');
    if (coll) coll.textContent = state.mainCollectibles;
  }

  function updateTransferBalances(animate) {
    const you = $('#transfer-you-balance');
    const friend = $('#transfer-friend-balance');
    if (you) {
      you.textContent = state.transferYouBalance;
      if (animate) {
        you.classList.add('balance-down');
        you.offsetHeight;
        setTimeout(() => you.classList.remove('balance-down'), 400);
      }
    }
    if (friend) {
      friend.textContent = state.transferFriendBalance;
      if (animate) {
        friend.classList.add('balance-up');
        friend.offsetHeight;
        setTimeout(() => friend.classList.remove('balance-up'), 400);
      }
    }
  }

  function updateTree() {
    const tree = $('#tree-visual');
    if (!tree) return;
    tree.setAttribute('data-stage', Math.min(state.treeStage, 5));
  }

  function checkCompletedSteps() {
    const s = state.completedSteps;
    state.treeStage = [s.receive, s.send, s.send10, s.fee, s.approve].filter(Boolean).length;
    if (state.treeStage >= 5) state.mainCollectibles = 1;
    updateTree();
    updateMainWallet();
    updateProgress();
    unlockSections();
  }

  function updateProgress() {
    const stage = state.treeStage;
    const icons = $$('.progress-icons span');
    icons.forEach((el, i) => {
      el.classList.toggle('icon-active', i <= stage);
    });
  }

  function unlockSections() {
    const unlocked = state.treeStage + 1;
    $$('[data-section]').forEach(section => {
      const n = parseInt(section.dataset.section, 10);
      section.classList.toggle('section-locked', n > unlocked);
      section.classList.toggle('section-unlocked', n <= unlocked);
    });
  }

  function openModal(id) {
    const m = $(id);
    if (m) {
      m.classList.add('open');
      m.setAttribute('aria-hidden', 'false');
    }
  }

  function closeModal(id) {
    const m = $(id);
    if (m) {
      m.classList.remove('open');
      m.setAttribute('aria-hidden', 'true');
    }
  }

  function copyToClipboard(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text);
    } else {
      const ta = document.createElement('textarea');
      ta.value = text;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand('copy');
      document.body.removeChild(ta);
    }
  }

  $('#main-address').textContent = addresses.main;
  $('#transfer-you-address').textContent = addresses.main;
  $('#transfer-friend-address').textContent = addresses.friend;

  $('#btn-copy-main')?.addEventListener('click', () => {
    copyToClipboard(addresses.main);
    const btn = $('#btn-copy-main');
    btn?.classList.add('copied');
    btn.textContent = '✓';
    setTimeout(() => {
      btn?.classList.remove('copied');
      btn.textContent = '📋';
    }, 1500);
  });

  $('#link-explorer-main')?.addEventListener('click', (e) => {
    e.preventDefault();
    $('#explorer-address').textContent = addresses.main;
    $('#explorer-balance').textContent = state.mainBalance + ' Demo Coins';
    $('#explorer-nfts').textContent = state.mainCollectibles;
    const list = $('#explorer-tx-list');
    if (list) {
      list.innerHTML = state.transactions.slice(-5).reverse().map(tx =>
        '<li>' + tx.hash + ' — ' + tx.amount + ' coins</li>'
      ).join('') || '<li>No transactions yet</li>';
    }
    openModal('#explorer-modal');
  });

  $('#btn-close-explorer')?.addEventListener('click', () => closeModal('#explorer-modal'));
  $('#explorer-modal')?.addEventListener('click', e => {
    if (e.target.id === 'explorer-modal') closeModal('#explorer-modal');
  });

  $('#btn-receive')?.addEventListener('click', () => {
    state.mainBalance += 25;
    state.completedSteps.receive = true;
    checkCompletedSteps();
    updateMainWallet('up');
  });

  $('#btn-send')?.addEventListener('click', () => {
    if (state.mainBalance <= 0) return;
    state.mainBalance = Math.max(0, state.mainBalance - 10);
    state.completedSteps.send = true;
    checkCompletedSteps();
    updateMainWallet('down');
  });

  $$('input[name="gas"]').forEach(radio => {
    radio.addEventListener('change', () => {
      state.gasLevel = parseInt(radio.value, 10);
      const feeEl = $('#fee-amount');
      if (feeEl) feeEl.textContent = getGasFee();
    });
  });

  $('#btn-send-10')?.addEventListener('click', () => {
    if (state.transferYouBalance < 10) return;
    const fee = getGasFee();
    if (state.transferYouBalance < 10 + fee) return;
    state.pendingTransfer = { amount: 10, fee };
    $('#confirm-from').textContent = addresses.main;
    $('#confirm-to').textContent = addresses.friend;
    $('#confirm-amount').textContent = '10 Demo Coins';
    $('#confirm-fee').textContent = fee + ' Demo Coin' + (fee !== 1 ? 's' : '');
    openModal('#confirm-modal');
  });

  $('#btn-confirm-cancel')?.addEventListener('click', () => {
    state.pendingTransfer = null;
    closeModal('#confirm-modal');
  });

  $('#btn-confirm-ok')?.addEventListener('click', () => {
    const p = state.pendingTransfer;
    if (!p) return;
    closeModal('#confirm-modal');
    const btn = $('#btn-send-10');
    const container = $('#coins-animation');
    const youCard = $('#transfer-you');
    const friendCard = $('#transfer-friend');
    if (!container || !youCard || !friendCard) return;
    btn.disabled = true;

    const rectYou = youCard.getBoundingClientRect();
    const rectFriend = friendCard.getBoundingClientRect();
    const startX = rectYou.left + rectYou.width / 2 - 12;
    const startY = rectYou.top + rectYou.height / 2 - 12;
    const endX = rectFriend.left + rectFriend.width / 2 - 12;
    const endY = rectFriend.top + rectFriend.height / 2 - 12;

    container.classList.add('active');
    container.innerHTML = '';
    for (let i = 0; i < 3; i++) {
      const coin = document.createElement('div');
      coin.className = 'coin-particle';
      coin.style.left = startX + (i * 8) + 'px';
      coin.style.top = startY + (i * 4) + 'px';
      coin.style.setProperty('--tx', (endX - startX) + 'px');
      coin.style.setProperty('--ty', (endY - startY) + 'px');
      coin.style.animationDelay = (i * 0.1) + 's';
      container.appendChild(coin);
    }

    const txHash = makeTxHash('tx-' + Date.now() + Math.random());
    const delay = getConfirmDelay();

    setTimeout(() => {
      state.transferYouBalance -= p.amount + p.fee;
      state.transferFriendBalance += p.amount;
      updateTransferBalances(true);
      state.completedSteps.send10 = true;
      state.transactions.push({
        hash: txHash,
        from: addresses.main,
        to: addresses.friend,
        amount: p.amount,
        fee: p.fee
      });
      checkCompletedSteps();

      const list = $('#transaction-list');
      if (list) {
        const item = document.createElement('div');
        item.className = 'tx-item';
        item.innerHTML = '<span class="tx-hash">' + txHash + '</span> <a class="tx-link" data-tx-index="' + (state.transactions.length - 1) + '">View Transaction</a>';
        list.appendChild(item);
        item.querySelector('.tx-link')?.addEventListener('click', function(e) {
          e.preventDefault();
          const idx = parseInt(this.dataset.txIndex, 10);
          const tx = state.transactions[idx];
          if (tx) {
            $('#tx-hash').textContent = tx.hash;
            $('#tx-from').textContent = tx.from;
            $('#tx-to').textContent = tx.to;
            $('#tx-amount').textContent = tx.amount + ' Demo Coins';
            $('#tx-fee').textContent = tx.fee + ' Demo Coin' + (tx.fee !== 1 ? 's' : '');
            $('#tx-status').textContent = 'Confirmed';
            openModal('#tx-modal');
          }
        });
      }
    }, 400);

    setTimeout(() => {
      container.classList.remove('active');
      container.innerHTML = '';
      btn.disabled = false;
      state.pendingTransfer = null;
    }, 1200);
  });

  $('#btn-why-fee')?.addEventListener('click', () => {
    openModal('#fee-modal');
    state.completedSteps.fee = true;
    checkCompletedSteps();
  });

  $('#btn-close-fee')?.addEventListener('click', () => closeModal('#fee-modal'));
  $('#fee-modal')?.addEventListener('click', e => {
    if (e.target.id === 'fee-modal') closeModal('#fee-modal');
  });

  $('#btn-approve')?.addEventListener('click', () => {
    const result = $('#approve-result');
    if (result) {
      result.textContent = '✓ Approved! You said yes to the action.';
      result.classList.remove('rejected');
      state.completedSteps.approve = true;
      checkCompletedSteps();
    }
  });

  $('#btn-reject')?.addEventListener('click', () => {
    const result = $('#approve-result');
    if (result) {
      result.textContent = 'Rejected. You chose not to allow this action.';
      result.classList.add('rejected');
      state.completedSteps.approve = true;
      checkCompletedSteps();
    }
  });

  $('#nft-clickable')?.addEventListener('click', () => {
    $('#nft-owner-address').textContent = addresses.main;
    openModal('#nft-modal');
  });

  $('#nft-clickable')?.addEventListener('keydown', e => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      $('#nft-owner-address').textContent = addresses.main;
      openModal('#nft-modal');
    }
  });

  $('#btn-close-nft')?.addEventListener('click', () => closeModal('#nft-modal'));
  $('#nft-modal')?.addEventListener('click', e => {
    if (e.target.id === 'nft-modal') closeModal('#nft-modal');
  });

  $('#btn-close-tx')?.addEventListener('click', () => closeModal('#tx-modal'));
  $('#tx-modal')?.addEventListener('click', e => {
    if (e.target.id === 'tx-modal') closeModal('#tx-modal');
  });

  $('#btn-garden')?.addEventListener('click', (e) => {
    e.preventDefault();
    alert("You're in the sandbox! In the real BrainBonsai app, this would take you back to your garden.");
  });

  updateMainWallet();
  updateTransferBalances();
  updateTree();
  unlockSections();
  updateProgress();
  $('#fee-amount').textContent = getGasFee();
})();
